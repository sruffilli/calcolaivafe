#!/usr/bin/env python3
"""
Calcolo Tasse Dividendi e IVAFE su Cash.
"""

import argparse
import csv
import os
import sys
from datetime import date, datetime, timedelta
import requests
import pandas as pd

# ---------------------------------------------------------------------------
# Cache in memoria per evitare chiamate API duplicate
# ---------------------------------------------------------------------------
_exchange_rate_cache = {}

# ---------------------------------------------------------------------------
# TASSO DI CAMBIO — Banca d'Italia REST API
# ---------------------------------------------------------------------------
def _fetch_exchange_rate_monthly(target_date: date) -> float | None:
    url = "https://tassidicambio.bancaditalia.it/terzevalute-wf-web/rest/v1.0/monthlyAverageRates"
    params = {
        "month": str(target_date.month).zfill(2),
        "year": str(target_date.year),
        "baseCurrencyIsoCode": "USD",
        "currencyIsoCode": "EUR",
        "lang": "it",
    }
    headers = {"Accept": "application/json"}
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", [])
        if rates:
            return float(rates[0]["avgRate"])
    except Exception:
        return None
    return None

def get_exchange_rate(target_date: date) -> float:
    cache_key = f"{target_date.year}_{target_date.month}"
    if cache_key in _exchange_rate_cache:
        return _exchange_rate_cache[cache_key]

    rate = _fetch_exchange_rate_monthly(target_date)
    if rate is None:
        raise ValueError(
            f"Impossibile recuperare il tasso di cambio mensile per {target_date.year}-{target_date.month}"
        )
    _exchange_rate_cache[cache_key] = rate
    return rate

def parse_cash(cash_str):
    if not cash_str: return 0.0
    s = (
        cash_str.replace("$", "")
        .replace("USD", "")
        .replace(" ", "")
        .replace(",", "")
    )
    if s.startswith("(") and s.endswith(")"):
        s = "-" + s[1:-1]
    try:
        return float(s)
    except ValueError:
        return 0.0

def main():
    parser = argparse.ArgumentParser(
        description="Calcolo tasse dividendi e IVAFE su cash direttamente dall'estratto conto."
    )
    parser.add_argument(
        "--csv", default="account-summary.csv", help="File CSV dell'estratto conto (es. account-summary.csv)"
    )
    parser.add_argument(
        "--anno", type=int, required=True, help="Anno fiscale di riferimento"
    )
    parser.add_argument(
        "--cutoff",
        type=lambda s: datetime.strptime(s, "%Y-%m-%d").date(),
        nargs="*",
        default=[],
        help="Date di cutover (YYYY-MM-DD) per azzerare il conto",
    )
    args = parser.parse_args()

    input_file = args.csv
    target_year = args.anno
    cutoffs = args.cutoff

    if not os.path.exists(input_file):
        print(f"Error: File {input_file} not found.")
        sys.exit(1)

    # We use all valid activities for the true cash balance
    exclude_activities = ["Opening Value", "Closing Value", "Opening Balance"]

    operations = []
    
    with open(input_file, mode="r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = None
        for row in reader:
            if not row: continue
            if row[0] == "Entry Date":
                header = row
                break
                
        if not header:
            print("Errore: Header 'Entry Date' non trovato nel CSV.")
            sys.exit(1)

        dict_reader = csv.DictReader(f, fieldnames=header)
        for row in dict_reader:
            entry_date_str = row.get("Entry Date", "").strip()
            if not entry_date_str or entry_date_str.startswith("Fund:"):
                continue
                
            try:
                act = row.get("Activity", "").strip()
                if act not in exclude_activities:
                    op_date = datetime.strptime(entry_date_str, "%d-%b-%Y").date()
                    amount = parse_cash(row.get("Cash", ""))
                    operations.append({
                        "date": op_date,
                        "activity": act,
                        "amount": amount
                    })
            except ValueError:
                pass

    if not operations:
        print("Nessuna operazione rilevante trovata.")
        sys.exit(0)

    # Sort operations by date
    operations.sort(key=lambda x: x["date"])

    # Combine operations and cutovers into events
    events = []
    for op in operations:
        events.append(
            {"date": op["date"], "type": "OP", "amount": op["amount"], "activity": op["activity"]}
        )
    for c in cutoffs:
        events.append({"date": c, "type": "CUT", "amount": 0, "activity": "Cutoff"})

    events.sort(key=lambda x: x["date"])

    # Track balance from the beginning
    balance = 0.0
    current_date = events[0]["date"]

    year_start = date(target_year, 1, 1)
    year_end = date(target_year, 12, 31)

    daily_balances = {}

    # Simulation end date: the end of the target year or the last event, whichever is later
    end_simulation = max(year_end, events[-1]["date"])
    
    sim_date = current_date
    event_idx = 0
    
    while sim_date <= end_simulation:
        # Process all events on this day
        while event_idx < len(events) and events[event_idx]["date"] == sim_date:
            ev = events[event_idx]
            if ev["type"] == "OP":
                balance += ev["amount"]
            elif ev["type"] == "CUT":
                balance = 0.0
            event_idx += 1
        
        daily_balances[sim_date] = balance
        sim_date += timedelta(days=1)

    # Calculate Giacenza Media and Picco Massimo for target_year in EUR
    sum_eur = 0.0
    picco_massimo_eur = 0.0
    
    # We iterate over all days of the target year
    for d in pd.date_range(start=year_start, end=year_end):
        d_date = d.date()
        usd_bal = daily_balances.get(d_date, 0.0)
        
        if usd_bal != 0.0:
            try:
                rate = get_exchange_rate(d_date)
                eur_bal = usd_bal / rate
            except ValueError:
                eur_bal = usd_bal
        else:
            eur_bal = 0.0
            
        sum_eur += eur_bal
        if eur_bal > picco_massimo_eur:
            picco_massimo_eur = eur_bal

    giacenza_media = sum_eur / 365.0

    # Calculate Dividends for Quadro RM in target_year
    sum_dividends_eur = 0.0
    count_ops = 0
    
    for op in operations:
        if op["date"].year == target_year and op["activity"] in ["Dividend (Cash)", "IRS Nonresident Alien Withholding"]:
            try:
                rate = get_exchange_rate(op["date"])
                eur_amount = op["amount"] / rate
            except ValueError:
                eur_amount = op["amount"]
            
            sum_dividends_eur += eur_amount
            
            if op["activity"] == "Dividend (Cash)":
                count_ops += 1

    # Output Results
    print("\n" + "=" * 60)
    print(f"  RISULTATI FISCALI PER L'ANNO {target_year}")
    print("=" * 60)
    
    print(f"\n[Quadro RW - Monitoraggio e IVAFE su Cash]")
    print(f"  Giacenza Media calcolata: €{giacenza_media:.2f}")
    print(f"  Picco Massimo nell'anno: €{picco_massimo_eur:.2f}")
    
    ivafe_cash = 0.0
    if giacenza_media > 5000:
        print("  -> SOGLIA 5.000€ SUPERATA!")
        print("  -> Dovuta IVAFE fissa di 34,20€ (da rapportare ai giorni di apertura se applicabile).")
        ivafe_cash = 34.20
    elif picco_massimo_eur > 15000:
        print("  -> SOGLIA 15.000€ SUPERATA! È obbligatorio dichiarare il conto nel Quadro RW ai fini del monitoraggio fiscale.")
        print("  -> Soglia 5.000€ non superata, quindi nessuna IVAFE dovuta.")
    else:
        print("  -> Giacenza media < 5.000€ E picco < 15.000€.")
        print("  -> Secondo la normativa vigente (L. 186/2014), NON vi è obbligo di dichiarare il conto nel Quadro RW.")
        
    print(f"\n[Quadro RM - Redditi di Capitale]")
    print(f"  Numero operazioni dividendo nel {target_year}: {count_ops}")
    print(f"  Totale Dividendi Netti (Netto Frontiera): €{sum_dividends_eur:.2f}")
    imposta_sostitutiva = 0.0
    if sum_dividends_eur > 0:
        imposta_sostitutiva = sum_dividends_eur * 0.26
        print(f"  -> Imposta sostitutiva dovuta (26%): €{imposta_sostitutiva:.2f}")
    print("=" * 60 + "\n")

    # Generazione CSV
    rm_filename = f"quadro_rm_{target_year}.csv"
    with open(rm_filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Anno", "Tipo Reddito", "Codice Stato Estero", "Totale Dividendi Netti (EUR)", "Imposta Sostitutiva 26% (EUR)"])
        if sum_dividends_eur > 0:
            writer.writerow([target_year, "L (Utili esteri)", "069", round(sum_dividends_eur, 2), round(imposta_sostitutiva, 2)])
    print(f"  Output CSV salvato in: {rm_filename}")

    rw_filename = f"quadro_rw_cash_{target_year}.csv"
    with open(rw_filename, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Anno", "Codice individuazione bene", "Codice Stato Estero", "Giacenza Media (EUR)", "Picco (EUR)", "IVAFE Dovuta", "Obbligo RW"])
        obbligo = "SI" if giacenza_media > 5000 or picco_massimo_eur > 15000 else "NO"
        writer.writerow([target_year, "1 (Conto Corrente)", "069", round(giacenza_media, 2), round(picco_massimo_eur, 2), ivafe_cash, obbligo])
    print(f"  Output CSV salvato in: {rw_filename}\n")

if __name__ == "__main__":
    main()
