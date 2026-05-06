---
name: calcola-ivafe
description: Skill per calcolare l'IVAFE e generare il Quadro RW con gestione avanzata di vendite totali (Rolling Cutoffs), supporto TSV e intervista guidata all'utente.
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
3.  **Vendite Singole**: "Hai effettuato vendite di singoli blocchi? In tal caso, è meglio aggiungere una colonna 'Sale Date' (o 'Data Vendita') nel CSV per una precisione millimetrica."

### 2. Funzionamento di Cutoffs e Sale Date
Spiega all'utente come lo script userà le date fornite:
- **Cutoffs Multipli**: Se vengono fornite più date di cutoff, lo script le ordina e assegna ogni azione al **primo cutoff** che si verifica alla data di maturazione o dopo di essa. Questo simula uno svuotamento periodico del conto.
- **Colonna Sale Date**: Se il file include una colonna `Sale Date` o `Data Vendita`, lo script userà quella data specifica come termine del possesso per quella riga. La data di vendita prevale sulla fine dell'anno se precedente.

### 3. Supporto File
- Lo script supporta sia file **CSV** che **TSV** (Tab-Separated Values).
- Rileva automaticamente il separatore e gestisce la presenza o meno di una riga di titolo iniziale tipica dei report di Morgan Stanley.

### 4. Esecuzione Tecnica
Configura l'ambiente e lancia lo script:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r .gemini/skills/calcola-ivafe/scripts/requirements.txt
```

> [!TIP]
> Se riscontri errori di autenticazione (401) durante l'installazione, prova a forzare l'indice pubblico:
> `uv pip install --index-url https://pypi.org/simple -r .gemini/skills/calcola-ivafe/scripts/requirements.txt`

**Esecuzione con cutoff multipli:**
```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv conca.tsv --anno 2024 --cutoff 2023-12-31 2024-06-15
```

## Parametri Script
- `--csv <path>`: Percorso del file (CSV o TSV).
- `--anno <YYYY>`: Anno fiscale.
- `--cutoff <YYYY-MM-DD> [...]`: Lista di date di liquidazione totale.
- `--ticker <TICKER>`: Default `GOOG`.

## Risultati
Lo script genera una tabella testuale e un file CSV (`quadro_rw_YYYY_TICKER.csv`). Verifica con l'utente se i giorni di possesso calcolati riflettono la sua situazione reale prima di considerare il compito concluso.
