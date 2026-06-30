---
name: calcola-ivafe
description: Skill per calcolare l'IVAFE per le stock, le imposte sui dividendi (Quadro RM) e l'IVAFE sulla liquidità accumulata (Quadro RW).
---

# Calcolo Fiscale Esteri (Quadro RW e RM) - Skill Locale

Questa skill automatizza il calcolo dell'imposta IVAFE italiana e la generazione delle righe per il Quadro RW e RM partendo da estratti conto di broker esteri.

## Struttura della Skill

I file si trovano nella radice del repository:
- `scripts/calcola_ivafe.py`: Lo script per il calcolo dell'IVAFE su azioni (GSUs).
- `scripts/calcola_dividendi.py`: Lo script per il calcolo delle tasse sui dividendi (Quadro RM) e IVAFE su cash (Quadro RW).
- `scripts/requirements.txt`: Dipendenze (pandas, yfinance, requests, tabulate).

## Documentazione di Riferimento
- [IVAFE.md](file:///Users/sruffilli/git/calcolaivafe/references/IVAFE.md): Report sull'architettura normativa dell'IVAFE.
- [DIVIDENDI.md](file:///Users/sruffilli/git/calcolaivafe/references/DIVIDENDI.md): Guida al calcolo dei dividendi esteri (Netto Frontiera).

## Flusso Operativo (Mandatorio)

### 1. Intervista Iniziale (Preparazione Dati)
> [!IMPORTANT]
> - Se l'utente non fornisce proattivamente l'anno fiscale o le date di cutoff nel prompt di invocazione, **devi richiederle esplicitamente**. **Non tentare di inferire** queste informazioni dal contesto o dai file.
> - Se i file di input (`ss.csv` o `activity-summary.csv`) non sono presenti nel workspace, **guida l'utente passo-passo** nel recupero dei dati da Morgan Stanley mostrando le istruzioni specifiche riportate sotto.

Prima di eseguire i calcoli, verifica la presenza dei file e raccogli i parametri necessari ponendo queste domande:

#### Verifica File di Ingressi (se mancanti):
Se uno o entrambi i file non sono presenti, mostra all'utente come scaricarli:

*   **Per `ss.csv` (Calcolo Azioni/IVAFE):**
    1. Accedi a **Morgan Stanley atWork**.
    2. Vai su **Activity** > **Reports** > **Your Alphabet Stock Statement**.
    3. Imposta: *Reporting Period* = `All available history`, *Currency* = `USD`, *Output Format* = `CSV`.
    4. Clicca su **Run Report**, scarica il file e salvalo come `ss.csv` nel progetto.

*   **Per `activity-summary.csv` (Calcolo Dividendi/Cash):**
    1. Accedi a **Morgan Stanley atWork**.
    2. Vai su **Activity** > **Reports** > **Account Summary**.
    3. Imposta: *Period Quick Select* = `All Available History`, spunta sia *Share & Cash Holdings* che *Equity Awards*, *View As* = `Web Page`, *Account Summary Type* = `Full`.
    4. Clicca su **Submit** e attendi la generazione.
    5. Scorri fino in fondo (un trucco veloce è cercare "IRS Nonresident Alien Withholding").
    6. Seleziona e copia tutta la tabella **Activity** (quella con colonne: *Entry Date, Activity, Type of Money, Cash, Number of Shares*, ecc.) partendo dall'intestazione fino alla fine.
    7. Incolla i dati in Excel/Sheets, esportali in **CSV** e salvali come `activity-summary.csv` nel progetto.

#### Domande per i Parametri:
**Per le Azioni (IVAFE Stocks):**
1.  **Anno Fiscale**: "Per quale anno dobbiamo calcolare l'IVAFE sulle azioni? (es. 2024)"
2.  **Eventi di Liquidazione Totale (Cutoffs)**: "Durante l'anno (o in quelli passati), ci sono stati momenti in cui hai venduto o trasferito **tutte** le azioni presenti nel conto? Se sì, dimmi le date."
3.  **Vendite Singole**: "Hai effettuato vendite di singoli blocchi? In tal caso, assicurati che il CSV contenga la colonna 'Sale Date' (o 'Data Vendita')."

**Per i Dividendi e Cash (Quadro RM e IVAFE Cash):**
4.  **File Estratto Conto**: "Assicurati di avere il file completo `activity-summary.csv`."
5.  **Date di Cutover Cash**: "Ci sono state date in cui il conto cash (dove si accumulano i dividendi) è stato svuotato o azzerato?"

### 2. Funzionamento di Cutoffs e Sale Date (Spiegazione all'Utente)
Spiega all'utente come lo script userà le date fornite:
- **Cutoffs Multipli (Stock)**: Lo script li usa per chiudere automaticamente le finestre di possesso delle azioni maturate fino a quel momento.
- **Cutoffs Cash**: Lo script resetta a zero il saldo accumulato da quella data in poi per il calcolo della giacenza media.

### 3. Esecuzione Tecnica
Configura l'ambiente e lancia gli script appropriati:

```bash
# Crea il venv solo se non esiste
[ -d .venv ] || uv venv .venv
source .venv/bin/activate
uv pip install -r scripts/requirements.txt
```

> [!TIP]
> Se riscontri errori di autenticazione (401) durante l'installazione, prova a forzare l'indice pubblico:
> `uv pip install --index-url https://pypi.org/simple -r scripts/requirements.txt`

**Esecuzione Calcolo Stock:**
```bash
python scripts/calcola_ivafe.py --csv report_azioni.csv --anno 2024 --account-summary account-summary.csv
```

**Esecuzione Calcolo Dividendi e IVAFE Cash:**
```bash
python scripts/calcola_dividendi.py --csv account-summary.csv --anno 2024 --cutoff 2024-10-01
```

## Risultati
Gli script generano tabelle testuali e file CSV (`quadro_rw_...csv` e `quadro_rm_...csv`). Verifica con l'utente se i risultati riflettono la sua situazione reale prima di considerare il compito concluso.
