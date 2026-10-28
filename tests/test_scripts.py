#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pandas",
#     "requests",
#     "yfinance",
#     "tabulate",
# ]
# ///
"""
Test automatici per calcola_ivafe.py e calcola_dividendi.py.

Nessuna rete: Banca d'Italia e Yahoo Finance sono sostituiti da funzioni
deterministiche, così i numeri attesi sono calcolabili a mano:
    cambio medio mensile   = 1 + mese/100      (gen 1.01 ... dic 1.12)
    cambio giornaliero     = 1 + giorno/1000   (il 17 del mese -> 1.017)
    prezzo di chiusura     = 100 + giorno_dell_anno/10
Gli script vengono eseguiti sui file *.csv.sample del repository e su piccole
fixture sintetiche scritte in una directory temporanea.
"""

import calendar
import contextlib
import csv
import importlib.util
import io
import logging
import os
import subprocess
import sys
import tempfile
import traceback
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


# ---------------------------------------------------------------------------
# Finti servizi esterni
# ---------------------------------------------------------------------------
def fx_monthly(d: date) -> float:
    return 1 + d.month / 100


def fx_daily(d: date) -> float:
    return 1 + d.day / 1000


def price(d: date) -> float:
    return 100 + d.timetuple().tm_yday / 10


class _FakeResp:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self):
        pass

    def json(self):
        return self._payload


def fake_requests_get(url, params=None, headers=None, timeout=None):
    params = params or {}
    if "monthlyAverageRates" in url:
        rate = fx_monthly(date(int(params["year"]), int(params["month"]), 1))
    elif "dailyRates" in url:
        rate = fx_daily(date.fromisoformat(params["referenceDate"]))
    else:
        raise AssertionError(f"URL inattesa: {url}")
    return _FakeResp({"rates": [{"avgRate": str(rate)}]})


def fake_yf_download(ticker, start=None, end=None, progress=False):
    idx = pd.date_range(start=start, end=pd.Timestamp(end) - timedelta(days=1))
    return pd.DataFrame({"Close": [price(d.date()) for d in idx]}, index=idx)


class _FakeTicker:
    def __init__(self, ticker):
        self.ticker = ticker

    def history(self, start=None, end=None):
        d = date.fromisoformat(start)
        return pd.DataFrame({"Close": [price(d)]}, index=[pd.Timestamp(d)])


requests.get = fake_requests_get
yf.download = fake_yf_download
yf.Ticker = _FakeTicker
logging.disable(logging.CRITICAL)  # i warning degli script sono verificati su stdout


# ---------------------------------------------------------------------------
# Harness
# ---------------------------------------------------------------------------
def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_main(mod, argv, cwd):
    """Esegue mod.main() con argv e cwd dati; restituisce (stdout, exit_code)."""
    old_argv, old_cwd = sys.argv, os.getcwd()
    buf = io.StringIO()
    code = 0
    try:
        sys.argv = [mod.__name__] + argv
        os.chdir(cwd)
        with contextlib.redirect_stdout(buf):
            try:
                mod.main()
            except SystemExit as e:
                code = int(e.code or 0)
    finally:
        sys.argv = old_argv
        os.chdir(old_cwd)
    return buf.getvalue(), code


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def close(a, b, tol=0.01):
    return abs(float(a) - float(b)) <= tol


FAILURES = []


def check(name, cond, detail=""):
    status = "ok" if cond else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------
def test_ivafe_sample(tmp):
    print("calcola_ivafe.py su ss.csv.sample + account-summary.csv.sample (2025)")
    mod = load("calcola_ivafe")
    out, code = run_main(mod, [
        "--csv", str(ROOT / "ss.csv.sample"), "--anno", "2025",
        "--account-summary", str(ROOT / "account-summary.csv.sample"),
    ], tmp)
    check("exit 0", code == 0, f"exit={code}")
    out_csv = Path(tmp) / "quadro_rw_2025_GOOG.csv"
    check("CSV scritto nella cwd", out_csv.exists())
    if not out_csv.exists():
        return
    rows = {r["Giorni (IVAFE)"]: r for r in read_csv(out_csv)}
    # SAMPLE001 (vest 2024-01-25) e' chiuso dal cutoff 2024-05-17: non compare.
    # SAMPLE002: 10 azioni, 2025-01-25 -> Sale Date 2025-06-30 = 157 giorni.
    # SAMPLE003: 7.5 azioni, 2025-03-25 -> 2025-12-31 = 282 giorni.
    check("due righe RW (157 e 282 giorni)", set(rows) == {"157", "282"}, str(set(rows)))
    if set(rows) != {"157", "282"}:
        return
    r = rows["157"]
    check("riga 157: valore iniziale", close(r["Valore iniziale"], 1014.85), r["Valore iniziale"])
    check("riga 157: valore finale", close(r["Valore finale"], 1114.15), r["Valore finale"])
    check("riga 157: IVAFE", close(r["IVAFE"], 0.96), r["IVAFE"])
    r = rows["282"]
    check("riga 282: valore iniziale", close(r["Valore iniziale"], 789.32), r["Valore iniziale"])
    check("riga 282: valore finale", close(r["Valore finale"], 914.06), r["Valore finale"])
    check("riga 282: IVAFE", close(r["IVAFE"], 1.41), r["IVAFE"])
    for r in rows.values():
        check("codici fissi RW", (r["Codice individuaz. bene"], r["Codice Stato estero"]) == ("2", "069"))
    check("cutoff rilevati stampati", "Rilevati cutoff" in out and "2024-05-17" in out)
    check("sample: trasferimenti parziali segnalati", "PARZIALE" in out)


def test_ivafe_total_cutoff_not_flagged(tmp):
    print("calcola_ivafe.py: un transfer out che svuota il conto non e' PARZIALE")
    summary = Path(tmp) / "summary_total.csv"
    summary.write_text(
        "Entry Date,Activity,Type of Money,Cash,Number of Shares,Share Price,Book Value,Market Value\n"
        "25-Jan-2024,Release (X),Employee,,5.0,,,\n"
        "17-May-2024,Transfer out,Employee,,-5.0,,,\n"
        "25-Jan-2025,Release (Y),Employee,,10.0,,,\n"
        "25-Mar-2025,Release (Z),Employee,,7.5,,,\n"
    )
    mod = load("calcola_ivafe")
    out, code = run_main(mod, [
        "--csv", str(ROOT / "ss.csv.sample"), "--anno", "2025",
        "--account-summary", str(summary),
    ], tmp)
    check("exit 0", code == 0)
    check("nessun PARZIALE", "PARZIALE" not in out)
    check("residuo +0.000 stampato", "residuo +0.000" in out)


def test_dividendi_sample(tmp):
    print("calcola_dividendi.py su account-summary.csv.sample (2025)")
    mod = load("calcola_dividendi")
    out, code = run_main(mod, ["--csv", str(ROOT / "account-summary.csv.sample"), "--anno", "2025"], tmp)
    check("exit 0", code == 0, f"exit={code}")
    rm = read_csv(Path(tmp) / "quadro_rm_2025.csv")
    rw = read_csv(Path(tmp) / "quadro_rw_cash_2025.csv")
    check("quadro_rm: una riga", len(rm) == 1)
    if rm:
        r = rm[0]
        check("dividendi lordi (cambio giornaliero)", close(r["Dividendi Lordi (EUR)"], 381.12), r["Dividendi Lordi (EUR)"])
        check("ritenuta estera", close(r["Ritenuta Estera (EUR)"], 57.16), r["Ritenuta Estera (EUR)"])
        check("dividendi netti", close(r["Dividendi Netti (EUR)"], 323.96), r["Dividendi Netti (EUR)"])
        check("imposta 26% sul lordo", close(r["Imposta Sostitutiva 26% su Lordo (EUR)"], 99.09))
        check("codice H, stato 069", r["Tipo Reddito"].startswith("H") and r["Codice Stato Estero"] == "069")
    check("cash sempre girato fuori: giacenza 0, nessun obbligo RW",
          rw and close(rw[0]["Giacenza Media (EUR)"], 0) and rw[0]["Obbligo RW"] == "NO")
    check("4 operazioni dividendo", "Numero operazioni dividendo nel 2025: 4" in out)


def test_giacenza_media_leap_year(tmp):
    print("calcola_dividendi.py: giacenza media / 365 anche in anno bisestile (2024)")
    summary = Path(tmp) / "summary_cash.csv"
    summary.write_text(
        "Entry Date,Activity,Type of Money,Cash,Number of Shares,Share Price,Book Value,Market Value\n"
        "01-Jan-2024,Dividend (Cash),Employee,\"$10,000.00 USD\",,,,\n"
    )
    mod = load("calcola_dividendi")
    out, code = run_main(mod, ["--csv", str(summary), "--anno", "2024"], tmp)
    check("exit 0", code == 0)
    rw = read_csv(Path(tmp) / "quadro_rw_cash_2024.csv")[0]
    # 10000 USD fermi tutto il 2024 (366 giorni), cambio mensile 1+m/100, /365
    expected = sum(10000 / fx_monthly(date(2024, m, 1)) * calendar.monthrange(2024, m)[1]
                   for m in range(1, 13)) / 365
    check("giacenza media = somma saldi / 365", close(rw["Giacenza Media (EUR)"], round(expected, 2)),
          f"{rw['Giacenza Media (EUR)']} vs {expected:.2f}")
    check("picco = 10000/1.01", close(rw["Picco (EUR)"], 9900.99), rw["Picco (EUR)"])
    check("soglia 5000 superata: IVAFE 34.20, obbligo RW",
          close(rw["IVAFE Dovuta"], 34.20) and rw["Obbligo RW"] == "SI")


def test_dividendi_fails_without_network(tmp):
    print("calcola_dividendi.py senza rete: errore esplicito, nessun output")
    env = dict(os.environ, HTTP_PROXY="http://127.0.0.1:9", HTTPS_PROXY="http://127.0.0.1:9",
               http_proxy="http://127.0.0.1:9", https_proxy="http://127.0.0.1:9", NO_PROXY="")
    p = subprocess.run(
        [sys.executable, str(SCRIPTS / "calcola_dividendi.py"),
         "--csv", str(ROOT / "account-summary.csv.sample"), "--anno", "2025"],
        cwd=tmp, env=env, capture_output=True, text=True, timeout=120,
    )
    check("exit 1", p.returncode == 1, f"exit={p.returncode}")
    check("messaggio 'Errore fatale' su stderr", "Errore fatale" in p.stderr, p.stderr[-300:])
    check("nessun CSV prodotto", not (Path(tmp) / "quadro_rm_2025.csv").exists())


def test_parse_html(tmp):
    print("parse_html_summary.py: tabella Activity -> CSV")
    mod = load("parse_html_summary")
    html = """<html><body><table>
    <tr><td>Entry Date</td><td>Activity</td><td>Type of Money</td><td>Cash</td>
        <td>Number of Shares</td><td>Share Price</td><td>Book Value</td><td>Market Value</td></tr>
    <tr><td colspan="8">Fund: Alphabet</td></tr>
    <tr><td>17-Mar-2025</td><td>Dividend (Cash)</td><td>Employee</td><td>$44.10 USD</td>
        <td></td><td></td><td></td><td></td></tr>
    <tr><td>25-Mar-2025</td><td>Release (ABC)</td><td>Employee</td><td></td>
        <td>7.5</td><td></td><td>$1,000.00 USD</td><td></td></tr>
    </table></body></html>"""
    rows = mod.parse_html(html)
    check("header Entry Date", rows[1][0] == "Entry Date" and len(rows[1]) == 8)
    check("riga Fund: conservata", rows[2][0] == "Fund: Alphabet")
    check("riga dividendo", rows[3][:4] == ["17-Mar-2025", "Dividend (Cash)", "Employee", "$44.10 USD"])
    check("riga release, 8 colonne", rows[4][4] == "7.5" and len(rows[4]) == 8)


def main():
    tests = [
        test_ivafe_sample, test_ivafe_total_cutoff_not_flagged, test_dividendi_sample,
        test_giacenza_media_leap_year, test_dividendi_fails_without_network, test_parse_html,
    ]
    for t in tests:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                t(tmp)
            except Exception:
                traceback.print_exc()
                FAILURES.append(t.__name__ + " (eccezione)")
    print()
    if FAILURES:
        print(f"FALLITI ({len(FAILURES)}): " + ", ".join(FAILURES))
        sys.exit(1)
    print("Tutti i test passano.")


if __name__ == "__main__":
    main()
