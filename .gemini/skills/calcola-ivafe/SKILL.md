---
name: calcola-ivafe
description: Skill per calcolare l'IVAFE e generare il Quadro RW con gestione avanzata di vendite totali (Rolling Cutoffs) e intervista guidata all'utente.
---

# Calcola IVAFE (Quadro RW) - Skill Locale

Questa skill automatizza il calcolo dell'imposta IVAFE italiana e la generazione delle righe per il Quadro RW partendo da un estratto conto GSU (es. Google).

## Struttura della Skill

I file della skill si trovano in `.gemini/skills/calcola-ivafe/scripts/`:
- `calcola_ivafe.py`: Lo script core con logica di aggregazione e calcolo fiscale.
- `requirements.txt`: Dipendenze (pandas, yfinance, requests, tabulate).

## Flusso Operativo (Mandatorio)

### 1. Intervista Iniziale (Preparazione Dati)
Prima di eseguire il calcolo, poni queste domande all'utente:
1.  **Anno Fiscale**: "Per quale anno dobbiamo calcolare l'IVAFE? (es. 2024)"
2.  **Eventi di Liquidazione Totale (Cutoffs)**: "Durante l'anno (o in quelli passati), ci sono stati momenti in cui hai venduto o trasferito **tutte** le azioni presenti nel conto? Se sì, dimmi le date."
    - *Spiegazione*: Questi sono i "Rolling Cutoffs". Lo script li usa per chiudere automaticamente le finestre di possesso delle azioni maturate fino a quel momento.
3.  **Vendite Singole**: "Hai effettuato vendite di singoli blocchi? In tal caso, è meglio aggiungere una colonna 'Sale Date' nel CSV per una precisione millimetrica."

### 2. Strategia "Rolling Cutoff"
Spiega all'utente come lo script userà le date fornite:
- Ogni cutoff `C` agisce come una data di vendita per tutte le azioni maturate prima di `C`.
- Se il cutoff cade nell'anno fiscale in analisi, pagherai le tasse solo per i giorni che precedono il cutoff.
- Esempio: Con cutoff `2025-06-30`, le azioni che avevi a inizio anno pagano solo 181 giorni di IVAFE.

### 3. Modifica CSV (Opzionale)
Offriti di assistere l'utente nella preparazione del file:
- Crea una copia del CSV originale (es. `ss_per_calcolo.csv`).
- Aggiungi le colonne `Sale Date` se necessario.
- Rettifica le quantità (`Shares Deposited`) se ci sono stati trasferimenti parziali non tracciabili con i cutoff.

### 4. Esecuzione Tecninca
Configura l'ambiente e lancia lo script:

```bash
uv venv --python 3.13 .venv
source .venv/bin/activate
uv pip install -r .gemini/skills/calcola-ivafe/scripts/requirements.txt
```

**Esecuzione con cutoff multipli:**
```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv ss.csv --anno 2024 --cutoff 2023-12-31 2024-06-15
```

## Parametri Script
- `--csv <path>`: Percorso del file.
- `--anno <YYYY>`: Anno fiscale.
- `--cutoff <YYYY-MM-DD> [...]`: Lista di date di liquidazione totale.
- `--ticker <TICKER>`: Default `GOOG`.

## Risultati
Lo script genera una tabella testuale e un file CSV (`quadro_rw_YYYY_TICKER.csv`). Verifica con l'utente se i giorni di possesso calcolati riflettono la sua situazione reale prima di considerare il compito concluso.
