---
name: calcola-ivafe
description: Skill per calcolare l'IVAFE per le stock, le imposte sui dividendi (Quadro RM) e l'IVAFE sulla liquidità accumulata (Quadro RW).
---

# Calcolo Fiscale Esteri (Quadro RW e RM) - Skill Locale

Questa skill automatizza il calcolo dell'imposta IVAFE italiana e la generazione delle righe per il Quadro RW e RM partendo da estratti conto di broker esteri.

## Struttura della Skill

I file della skill si trovano in `.gemini/skills/calcola-ivafe/scripts/`:
- `calcola_ivafe.py`: Lo script per il calcolo dell'IVAFE su azioni (GSUs).
- `calcola_dividendi.py`: Lo script per il calcolo delle tasse sui dividendi (Quadro RM) e IVAFE su cash (Quadro RW).
- `requirements.txt`: Dipendenze (pandas, yfinance, requests, tabulate).

## Documentazione di Riferimento
- [IVAFE.md](file:///Users/sruffilli/git/calcolaivafe/.gemini/skills/calcola-ivafe/references/IVAFE.md): Report sull'architettura normativa dell'IVAFE.
- [DIVIDENDI.md](file:///Users/sruffilli/git/calcolaivafe/.gemini/skills/calcola-ivafe/references/DIVIDENDI.md): Guida al calcolo dei dividendi esteri (Netto Frontiera).

## Flusso Operativo (Mandatorio)

### 1. Intervista Iniziale (Preparazione Dati)
Prima di eseguire i calcoli, poni queste domande all'utente per raccogliere i parametri necessari:

**Per le Azioni (IVAFE Stocks):**
1.  **Anno Fiscale**: "Per quale anno dobbiamo calcolare l'IVAFE sulle azioni? (es. 2024)"
2.  **Eventi di Liquidazione Totale (Cutoffs)**: "Durante l'anno (o in quelli passati), ci sono stati momenti in cui hai venduto o trasferito **tutte** le azioni presenti nel conto? Se sì, dimmi le date."
3.  **Vendite Singole**: "Hai effettuato vendite di singoli blocchi? In tal caso, assicurati che il CSV contenga la colonna 'Sale Date' (o 'Data Vendita')."

**Per i Dividendi e Cash (Quadro RM e IVAFE Cash):**
4.  **File Estratto Conto**: "Assicurati di avere il file completo `account-summary.csv`."
5.  **Date di Cutover Cash**: "Ci sono state date in cui il conto cash (dove si accumulano i dividendi) è stato svuotato o azzerato?"

### 2. Funzionamento di Cutoffs e Sale Date (Spiegazione all'Utente)
Spiega all'utente come lo script userà le date fornite:
- **Cutoffs Multipli (Stock)**: Lo script li usa per chiudere automaticamente le finestre di possesso delle azioni maturate fino a quel momento.
- **Cutoffs Cash**: Lo script resetta a zero il saldo accumulato da quella data in poi per il calcolo della giacenza media.

### 3. Esecuzione Tecnica
Configura l'ambiente e lancia gli script appropriati:

```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r .gemini/skills/calcola-ivafe/scripts/requirements.txt
```

> [!TIP]
> Se riscontri errori di autenticazione (401) durante l'installazione, prova a forzare l'indice pubblico:
> `uv pip install --index-url https://pypi.org/simple -r .gemini/skills/calcola-ivafe/scripts/requirements.txt`

**Esecuzione Calcolo Stock:**
```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv report_azioni.csv --anno 2024 --cutoff 2023-12-31 2024-06-15
```

**Esecuzione Calcolo Dividendi e IVAFE Cash:**
```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_dividendi.py --csv account-summary.csv --anno 2024 --cutoff 2024-10-01
```

## Risultati
Gli script generano tabelle testuali e file CSV (`quadro_rw_...csv` e `quadro_rm_...csv`). Verifica con l'utente se i risultati riflettono la sua situazione reale prima di considerare il compito concluso.
