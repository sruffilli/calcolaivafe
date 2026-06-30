#!/usr/bin/env python3
"""
Calcolo IVAFE per Quadro RW - Dichiarazione dei redditi italiana.

Script per il calcolo automatizzato dell'imposta IVAFE su azioni estere
(Alphabet/Google GSUs) e preparazione delle righe per il Quadro RW.

Utilizzo:
    python calcola_ivafe.py --csv ss.csv [--anno 2024] [--cutoff 2022-12-25] [--vendita 2025-06-15] [--ticker GOOG]

NOTE IMPORTANTI:
    - Se sono state effettuate vendite parziali di azioni, è consigliabile
      modificare il CSV in input per riflettere correttamente il numero di
      azioni ancora in deposito. Questo script assume che la data di vendita
      (--vendita) si applichi a TUTTE le azioni in blocco.
    - Per vendite parziali, creare un CSV separato con solo le azioni vendute
      e uno con quelle ancora in deposito, e lanciare lo script separatamente.
"""

import argparse
import calendar
import logging
import sys
from datetime import datetime, timedelta, date
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf
from tabulate import tabulate

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cache in memoria per evitare chiamate API duplicate
# ---------------------------------------------------------------------------
_exchange_rate_cache: dict[str, float] = {}
_stock_price_cache: dict[str, float] = {}

# ---------------------------------------------------------------------------
# Costanti Quadro RW
# ---------------------------------------------------------------------------
CODICE_TITOLO_POSSESSO = "1"   # 1 = Proprietà
VEDERE_ISTRUZIONI = "2"
CODICE_INDIVIDUAZ_BENE = "2"   # 2 = Titoli esteri
CODICE_STATO_ESTERO = "069"    # 069 = USA
QUOTA_POSSESSO = "100"         # 100%
CRITERIO_DETERMIN_VALORE = "1" # 1 = Valore di mercato
ALIQUOTA_IVAFE = 0.002         # 0.2% (White List)

# ---------------------------------------------------------------------------
# Mapping colonne CSV — cerchiamo per NOME, mai per posizione
# ---------------------------------------------------------------------------
REQUIRED_COLUMNS = {
    "vesting_date": "Vesting Date",
    "shares_deposited": "Shares Deposited",
    "currency": "Currency",
}

# Colonne opzionali
OPTIONAL_COLUMNS = {
    "sale_date": ["Sale Date", "Data Vendita"],
}


# ===================================================================
# FUNZIONI HELPER
# ===================================================================

def is_leap_year(year: int) -> bool:
    """Restituisce True se l'anno è bisestile."""
    return calendar.isleap(year)


def days_in_year(year: int) -> int:
    """Restituisce 366 se bisestile, 365 altrimenti."""
    return 366 if is_leap_year(year) else 365


def calculate_days(start: date, end: date) -> int:
    """Calcola il numero di giorni tra due date (inclusivo di entrambe)."""
    return (end - start).days + 1


def _try_previous_days(target_date: date, fetch_fn, source_name: str,
                       max_retries: int = 10):
    """
    Tenta di recuperare un dato per target_date. Se non disponibile,
    prova i giorni lavorativi precedenti fino a max_retries tentativi.
    """
    current = target_date
    for attempt in range(max_retries):
        try:
            value = fetch_fn(current)
            if value is not None:
                if current != target_date:
                    logger.warning(
                        "Dato %s per %s non trovato, utilizzo %s (-%d giorni)",
                        source_name, target_date.isoformat(),
                        current.isoformat(), attempt,
                    )
                return value
        except Exception as e:
            logger.debug("Tentativo %d fallito per %s (%s): %s", attempt, current, source_name, e)
            pass
        current -= timedelta(days=1)

    raise ValueError(
        f"Impossibile recuperare {source_name} per {target_date.isoformat()} "
        f"(tentati {max_retries} giorni precedenti)"
    )


# ===================================================================
# TASSO DI CAMBIO — Banca d'Italia REST API
# ===================================================================

def _fetch_exchange_rate_monthly(target_date: date) -> float | None:
    """
    Chiama l'API REST della Banca d'Italia per ottenere il tasso medio mensile EUR/USD.
    """
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
    except Exception:
        return None

    rates = data.get("rates", [])
    if not rates:
        return None

    return float(rates[0]["avgRate"])


def get_exchange_rate(target_date: date) -> float:
    """
    Restituisce il tasso EUR/USD (media mensile) dalla Banca d'Italia.
    Utilizza la cache in memoria per evitare chiamate ridondanti.
    """
    cache_key = f"{target_date.year}_{target_date.month}"
    if cache_key in _exchange_rate_cache:
        return _exchange_rate_cache[cache_key]

    rate = _fetch_exchange_rate_monthly(target_date)
    if rate is None:
        raise ValueError(
            f"Impossibile recuperare il tasso di cambio mensile per {target_date.year}-{target_date.month}"
        )

    logger.info(
        "Tasso EUR/USD (media mensile) per %d-%02d: %.4f (1 USD = %.4f EUR)",
        target_date.year, target_date.month, rate, 1/rate,
    )
    _exchange_rate_cache[cache_key] = rate
    return rate


# ===================================================================
# ESTRAZIONE CUTOFF DA ACCOUNT SUMMARY
# ===================================================================

def extract_cutoffs_from_summary(summary_path: str) -> list[date]:
    """
    Legge l'account summary e estrae le date dei 'Transfer out' o 'Sell' di azioni.
    """
    try:
        df = pd.read_csv(summary_path, sep=None, engine='python', dtype=str)
    except Exception as e:
        logger.error("Errore nella lettura dell'account summary: %s", e)
        return []

    col_date = None
    col_activity = None
    col_shares = None
    
    for col in df.columns:
        cleaned = col.strip().lower()
        if cleaned == 'entry date':
            col_date = col
        elif cleaned == 'activity':
            col_activity = col
        elif cleaned == 'number of shares':
            col_shares = col

    if not (col_date and col_activity and col_shares):
        # Tenta saltando la prima riga (caso report con intestazione)
        try:
            df = pd.read_csv(summary_path, sep=None, engine='python', dtype=str, skiprows=1)
            for col in df.columns:
                cleaned = col.strip().lower()
                if cleaned == 'entry date':
                    col_date = col
                elif cleaned == 'activity':
                    col_activity = col
                elif cleaned == 'number of shares':
                    col_shares = col
        except Exception:
            pass

    if not (col_date and col_activity and col_shares):
        logger.warning("Colonne necessarie non trovate in %s. Impossibile estrarre cutoff automaticamente.", summary_path)
        return []

    # Filtra per trasferimenti o vendite di azioni
    valid_activities = ['transfer out', 'sell', 'sale']
    df_transfers = df[df[col_activity].str.strip().str.lower().isin(valid_activities)].copy()
    
    # Converte le date
    df_transfers['parsed_date'] = pd.to_datetime(
        df_transfers[col_date].str.strip(), format="%d-%b-%Y", errors='coerce'
    ).dt.date
    
    df_transfers = df_transfers.dropna(subset=['parsed_date'])
    
    cutoff_dates = sorted(list(df_transfers['parsed_date'].unique()))
    return cutoff_dates


# ===================================================================
# PREZZO AZIONE — yfinance
# ===================================================================

def _fetch_stock_price_raw(target_date: date, ticker: str = "GOOG") -> float | None:
    """
    Recupera il prezzo di chiusura di un titolo da yfinance per una data.
    """
    start = target_date
    end = target_date + timedelta(days=1)

    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(start=start.isoformat(), end=end.isoformat())
        if hist.empty:
            return None
        return float(hist["Close"].iloc[0])
    except Exception:
        return None


def get_stock_price(target_date: date, ticker: str = "GOOG") -> float:
    """
    Restituisce il prezzo di chiusura del titolo per la data.
    Utilizza la cache in memoria per evitare chiamate ridondanti.
    """
    cache_key = f"{ticker}_{target_date.isoformat()}"
    if cache_key in _stock_price_cache:
        return _stock_price_cache[cache_key]

    def fetcher(d):
        return _fetch_stock_price_raw(d, ticker)

    price = _try_previous_days(
        target_date, fetcher, f"prezzo {ticker}"
    )

    logger.info(
        "Prezzo %s al %s: $%.2f",
        ticker, target_date.isoformat(), price,
    )
    _stock_price_cache[cache_key] = price
    return price


# ===================================================================
# PARSING CSV
# ===================================================================

def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Carica il CSV o TSV dell'estratto conto GSU.
    - Rileva automaticamente il separatore
    - Gestisce la presenza o meno di una riga di titolo iniziale
    - Identifica le colonne per NOME (non per posizione)
    - Pulisce i dati numerici e le date
    """
    # Tenta di leggere senza saltare righe
    try:
        df = pd.read_csv(csv_path, sep=None, engine='python', dtype=str)
    except Exception as e:
        logger.error("Errore nella lettura del file: %s", e)
        raise e

    # Controlla se le colonne richieste sono presenti
    # Altrimenti tenta di saltare la prima riga (caso report con titolo)
    required_found = all(any(col.strip().lower() == name.lower() for col in df.columns) 
                         for name in REQUIRED_COLUMNS.values())
    
    if not required_found:
        logger.info("Colonne richieste non trovate. Tento saltando la prima riga...")
        df = pd.read_csv(csv_path, sep=None, engine='python', dtype=str, skiprows=1)
        
    available_cols = list(df.columns)
    col_map = {}

    # Mappa colonne obbligatorie
    for key, expected_name in REQUIRED_COLUMNS.items():
        found = False
        for col in available_cols:
            if col.strip().lower() == expected_name.lower():
                col_map[key] = col
                found = True
                break
        if not found:
            raise ValueError(
                f"Colonna '{expected_name}' non trovata nel CSV. "
                f"Colonne disponibili: {available_cols}"
            )

    # Cerca colonna opzionale Sale Date
    for key, names in OPTIONAL_COLUMNS.items():
        for col in available_cols:
            if col.strip().lower() in [n.lower() for n in names]:
                col_map[key] = col
                break

    logger.info("Mapping colonne CSV: %s", col_map)

    # Filtra solo le righe con dati validi
    df = df.dropna(subset=[col_map["vesting_date"]])
    # Rimuovi righe che non hanno date valide (disclaimer, note, ecc.)
    df = df[df[col_map["vesting_date"]].str.match(
        r"^\d{2}-[A-Za-z]{3}-\d{4}$", na=False
    )]

    # Parse Vesting Date (formato DD-Mon-YYYY, es. "25-Apr-2026")
    df["vesting_date"] = pd.to_datetime(
        df[col_map["vesting_date"]], format="%d-%b-%Y"
    ).dt.date

    # Parse Sale Date se presente
    if "sale_date" in col_map:
        # Tenta diversi formati comuni o lascia che pandas indovini
        df["sale_date"] = pd.to_datetime(df[col_map["sale_date"]], errors="coerce").dt.date
        logger.info("Trovate %d date di vendita nel CSV", df["sale_date"].notna().sum())
    else:
        df["sale_date"] = None

    # Pulisci Shares Deposited: rimuovi $, virgole, spazi
    shares_col = df[col_map["shares_deposited"]].astype(str)
    shares_col = shares_col.str.replace("$", "", regex=False)
    shares_col = shares_col.str.replace(",", "", regex=False)
    shares_col = shares_col.str.strip()
    df["shares_deposited"] = pd.to_numeric(shares_col, errors="coerce")

    # Verifica Currency
    if col_map["currency"] in df.columns:
        non_usd = df[df[col_map["currency"]].str.strip().str.upper() != "USD"]
        if not non_usd.empty:
            logger.warning(
                "Trovate %d righe con valuta diversa da USD — verranno ignorate",
                len(non_usd),
            )
            df = df[df[col_map["currency"]].str.strip().str.upper() == "USD"]

    # Rimuovi righe con shares NaN
    df = df.dropna(subset=["shares_deposited"])
    df = df[df["shares_deposited"] > 0]

    logger.info("Caricate %d righe valide dal CSV", len(df))
    cols = ["vesting_date", "shares_deposited", "sale_date"]
    if "Purno" in df.columns:
        cols.append("Purno")
    return df[cols].reset_index(drop=True)


# ===================================================================
# LOGICA DI CALCOLO IVAFE
# ===================================================================

def compute_ivafe(df: pd.DataFrame, anno_fiscale: int, ticker: str = "GOOG",
                  cutoffs: list[date] | None = None) -> pd.DataFrame:
    """
    Calcola l'IVAFE per le azioni nel DataFrame.
    """
    anno_start = date(anno_fiscale, 1, 1)
    anno_end = date(anno_fiscale, 12, 31)
    
    # Punto 3: Denominatore giorni
    # Gli esempi delle istruzioni Quadro RW (es. Fascicolo 2 2026) usano il rapporto giorni/365
    # anche per anni bisestili, per standardizzare il calcolo.
    total_days = 365

    # --- Pre-caricamento prezzi azioni ---
    preload_start = anno_start - timedelta(days=15)
    preload_end = anno_end + timedelta(days=2)
    
    logger.info("Pre-caricamento prezzi delle azioni per %s dal %s al %s", ticker, preload_start.isoformat(), preload_end.isoformat())
    try:
        stock_data = yf.download(ticker, start=preload_start.isoformat(), end=preload_end.isoformat(), progress=False)
        if not stock_data.empty:
            # Reindicizza su tutti i giorni di calendario e propaga i valori (ffill)
            all_dates = pd.date_range(start=preload_start, end=preload_end - timedelta(days=1))
            stock_data = stock_data.reindex(all_dates, method='ffill')
            # Popola la cache
            for d, row in stock_data.iterrows():
                try:
                    close_val = row['Close']
                    if isinstance(close_val, pd.Series):
                        price = float(close_val.iloc[0])
                    else:
                        price = float(close_val)
                        
                    if not pd.isna(price):
                        _stock_price_cache[f"{ticker}_{d.date().isoformat()}"] = price
                except Exception as e:
                    logger.debug("Impossibile analizzare il prezzo per %s: %s", d, e)
    except Exception as e:
        logger.warning("Pre-caricamento dei prezzi fallito: %s. Si procede in modalità lenta.", e)

    # 1. Ignora azioni maturate DOPO la fine dell'anno fiscale
    df = df[df["vesting_date"] <= anno_end].copy()
    
    if df.empty:
        logger.warning("Nessuna azione valida per l'anno fiscale %d", anno_fiscale)
        return pd.DataFrame()

    # Ordiniamo i cutoff per la logica delle finestre
    sorted_cutoffs = sorted(cutoffs) if cutoffs else []

    # 3. Determina data finale per ogni riga in base ai cutoff
    def get_final_date(row):
        v = row["vesting_date"]
        # La data finale è il primo evento di chiusura (cutoff o vendita) 
        # che avviene alla data di maturazione o dopo.
        
        # Cerchiamo il primo cutoff >= v
        next_cutoff = None
        for c in sorted_cutoffs:
            if c >= v:
                next_cutoff = c
                break
        
        # Candidati per la data finale: 
        # - Il prossimo cutoff (se esiste)
        # - La data di vendita nel CSV (se presente)
        # - La fine dell'anno fiscale
        candidates = [anno_end]
        if next_cutoff:
            candidates.append(next_cutoff)
        
        csv_sale_date = row.get("sale_date")
        if pd.notna(csv_sale_date):
            candidates.append(csv_sale_date)
            
        return min(candidates)

    df["data_finale"] = df.apply(get_final_date, axis=1)
    df["is_pre_anno"] = df["vesting_date"] < anno_start

    # Rimuovi azioni maturate dopo la propria data di vendita (errori CSV)
    invalid = df[df["vesting_date"] > df["data_finale"]]
    if not invalid.empty:
        logger.warning("Escluse %d righe maturate dopo la loro data di vendita", len(invalid))
        df = df[df["vesting_date"] <= df["data_finale"]].copy()

    # --- Calcolo IVAFE per riga ---
    rows_ivafe = []
    for _, row in df.iterrows():
        vd = row["vesting_date"]
        dfin = row["data_finale"]
        shares = row["shares_deposited"]
        
        # Intervallo di possesso nell'anno fiscale
        data_inizio = max(row["vesting_date"], anno_start)
        data_finale = row["data_finale"]
        
        # Se la data finale è prima dell'inizio dell'anno, giorni = 0
        if data_finale < data_inizio:
            continue
            
        try:
            price_start = get_stock_price(data_inizio, ticker)
            price_end = get_stock_price(data_finale, ticker)
            
            # Punto 1: Tasso di cambio iniziale
            # Circolare 10/E/2014, punto 13.4: per le attività detenute al 1° gennaio si usa il cambio medio del mese di dicembre dell'anno precedente.
            if row["is_pre_anno"]:
                fx_start = get_exchange_rate(date(anno_fiscale - 1, 12, 31))
            else:
                fx_start = get_exchange_rate(data_inizio)
                
            fx_end = get_exchange_rate(data_finale)
        except ValueError as e:
            logger.warning("Salto la riga per %s a causa di un errore nel recupero dati: %s", row.get("Purno", "N/A"), e)
            continue

        # Punto 2: Valore iniziale per nuovi acquisti
        # Istruzioni Quadro RW (Fascicolo 2 2026, Colonna 7): indicare il valore all'inizio del periodo d'imposta
        # o al primo giorno di detenzione dell'attività. Quindi per i nuovi acquisti calcoliamo il valore alla data di inizio.
        vi = shares * price_start / fx_start
            
        vf = shares * price_end / fx_end
        giorni_ivafe = calculate_days(data_inizio, data_finale)
        if giorni_ivafe <= 0:
            continue
        ivafe = vf * ALIQUOTA_IVAFE * giorni_ivafe / total_days

        rows_ivafe.append({
            "is_pre_anno": row["is_pre_anno"],
            "data_finale": data_finale,
            "vi": vi,
            "vf": vf,
            "ivafe": ivafe
        })

    if not rows_ivafe:
        return pd.DataFrame()
    rdf = pd.DataFrame(rows_ivafe)

    # --- Aggregazione ---
    summary = rdf.groupby(["is_pre_anno", "data_finale"]).agg({
        "vi": "sum",
        "vf": "sum",
        "ivafe": "sum"
    }).reset_index()

    results = []
    for _, row in summary.sort_values(["is_pre_anno", "data_finale"], ascending=[False, True]).iterrows():
        vi = round(row["vi"], 2)
        vf = round(row["vf"], 2)
        ivafe = round(row["ivafe"], 2)

        # Back-calculate giorni per coerenza visiva nel Quadro RW
        if vf > 0 and ivafe > 0:
            giorni = round(ivafe * total_days / (vf * ALIQUOTA_IVAFE))
        else:
            if row["is_pre_anno"]:
                giorni = calculate_days(anno_start, row["data_finale"])
            else:
                giorni = 0 

        results.append({
            "Codice titolo possesso": CODICE_TITOLO_POSSESSO,
            "Vedere istruzioni": VEDERE_ISTRUZIONI,
            "Codice individuaz. bene": CODICE_INDIVIDUAZ_BENE,
            "Codice Stato estero": CODICE_STATO_ESTERO,
            "Quota di possesso": QUOTA_POSSESSO,
            "Criterio determin valore": CRITERIO_DETERMIN_VALORE,
            "Valore iniziale": vi,
            "Valore finale": vf,
            "Giorni (IVAFE)": giorni,
            "IVAFE": ivafe,
        })

    return pd.DataFrame(results)


# ===================================================================
# CLI
# ===================================================================

def parse_date(date_str: str) -> date:
    """Parse una data in formato YYYY-MM-DD."""
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Data '{date_str}' non valida. Usare il formato YYYY-MM-DD."
        )


def build_parser() -> argparse.ArgumentParser:
    default_anno = datetime.now().year - 1

    parser = argparse.ArgumentParser(
        description=(
            "Calcolo IVAFE per Quadro RW — Dichiarazione dei redditi italiana.\n\n"
            "  python calcola_ivafe.py --csv ss.csv\n"
            "  python calcola_ivafe.py --csv ss.csv --anno 2024\n"
            "  python calcola_ivafe.py --csv ss.csv --anno 2024 "
            "--cutoff 2023-06-30 2024-06-30\n\n"
            "NOTE:\n"
            "  - Lo script supporta più date di --cutoff. Ogni cutoff rappresenta\n"
            "    una liquidazione totale delle azioni maturate fino a quel momento.\n"
            "  - Lo script supporta una colonna 'Sale Date' o 'Data Vendita' nel CSV.\n"
            "  - Senza date specifiche, le azioni si considerano possedute fino al 31 Dicembre."
        ),
    )
    parser.add_argument(
        "--csv", required=True,
        help="Percorso del file CSV con l'estratto conto GSU.",
    )
    parser.add_argument(
        "--anno", type=int, default=default_anno,
        help=(
            f"Anno fiscale di riferimento (default: {default_anno})."
        ),
    )
    parser.add_argument(
        "--cutoff", type=parse_date, nargs="+", default=None,
        help=(
            "Date di cutoff (YYYY-MM-DD). Supporta date multiple. "
            "Ogni data agisce come evento di vendita totale per le azioni "
            "maturate dopo il cutoff precedente."
        ),
    )
    parser.add_argument(
        "--account-summary", default=None,
        help="Percorso del file CSV dell'account summary (es. activity-summary.csv) per rilevare automaticamente i cutoff.",
    )
    parser.add_argument(
        "--ticker", default="GOOG",
        help="Ticker del titolo su Yahoo Finance (default: GOOG).",
    )
    parser.add_argument(
        "--loglevel", default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Livello di logging (default: WARNING).",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # Configura logging
    numeric_level = getattr(logging, args.loglevel.upper(), None)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    try:
        # Validazioni
        csv_path = Path(args.csv)
        if not csv_path.exists():
            logger.error("File CSV non trovato: %s", csv_path)
            sys.exit(1)

        logger.info("=" * 60)
        logger.info("CALCOLO IVAFE — Quadro RW")
        logger.info("=" * 60)
        logger.info("CSV input:     %s", csv_path)
        logger.info("Anno fiscale:  %d", args.anno)
        logger.info("Ticker:        %s", args.ticker)
        
        # Gestione Cutoffs (Manuali + Automatici)
        cutoffs = args.cutoff or []
        if args.account_summary:
            detected_cutoffs = extract_cutoffs_from_summary(args.account_summary)
            if detected_cutoffs:
                print(f"\n[i] Rilevati cutoff in {args.account_summary}:")
                for d in detected_cutoffs:
                    print(f"    - {d.isoformat()}")
                cutoffs = sorted(list(set(cutoffs + detected_cutoffs)))
            else:
                print(f"\n[i] Nessun cutoff rilevato in {args.account_summary}")
        
        if args.cutoff:
            print(f"[i] Cutoffs inseriti manualmente: {', '.join([d.isoformat() for d in args.cutoff])}")
        logger.info(
            "Anno bisestile: %s (%d giorni)",
            "Sì" if is_leap_year(args.anno) else "No",
            days_in_year(args.anno),
        )
        logger.info("=" * 60)

        # Carica CSV
        df = load_csv(str(csv_path))

        # Calcola IVAFE
        result = compute_ivafe(
            df,
            anno_fiscale=args.anno,
            ticker=args.ticker,
            cutoffs=cutoffs,
        )

        if result.empty:
            logger.warning("Nessun risultato da esportare.")
            sys.exit(0)

        # Stampa formattata a schermo
        print("\n")
        print("=" * 80)
        print(f"  QUADRO RW — IVAFE Anno Fiscale {args.anno}")
        if cutoffs:
            print(f"  Cutoffs applicati: {', '.join([d.isoformat() for d in cutoffs])}")
        print("=" * 80)
        print(
            tabulate(
                result,
                headers="keys",
                tablefmt="fancy_grid",
                showindex=False,
                numalign="right",
                stralign="center",
                floatfmt=".2f"
            )
        )
        print("=" * 80)

        # Riepilogo
        ivafe_totale = result["IVAFE"].sum()
        print(f"\n  IVAFE TOTALE: €{ivafe_totale:.2f}")
        print("=" * 80)

        # Export CSV
        output_name = f"quadro_rw_{args.anno}_{args.ticker}.csv"
        output_path = csv_path.parent / output_name
        result.to_csv(output_path, index=False)
        logger.info("Risultati esportati in: %s", output_path)
        print(f"\n  Output CSV salvato in: {output_path}\n")
    except Exception as e:
        logger.error("Errore fatale durante l'esecuzione: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
