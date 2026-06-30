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
- `scripts/parse_html_summary.py`: Utility per convertire l'HTML dell'Account Summary in CSV.
- `scripts/requirements.txt`: Dipendenze (pandas, yfinance, requests, tabulate).

## Documentazione di Riferimento
- [IVAFE.md](../../../references/IVAFE.md): Report sull'architettura normativa dell'IVAFE.
- [DIVIDENDI.md](../../../references/DIVIDENDI.md): Guida al calcolo dei dividendi esteri (Netto Frontiera).

## Flusso Operativo (Mandatorio)

### 1. Intervista Iniziale (Preparazione Dati)
> [!IMPORTANT]
> - Se l'utente non fornisce proattivamente l'anno fiscale o le date di cutoff nel prompt di invocazione, **devi richiederle esplicitamente**. **Non tentare di inferire** queste informazioni dal contesto o dai file.
> - Segui il flusso decisionale sotto per determinare quali domande porre all'utente.

#### Flusso di Verifica e Intervista:

1.  **Verifica la presenza di `ss.csv`**:
    *   Se **manca**, mostra le istruzioni per scaricarlo (Vedi *Istruzioni ss.csv* sotto) e attendi che l'utente lo carichi.

2.  **Verifica la presenza di `activity-summary.csv` (o `account-summary.csv`)**:
    *   Se **è presente**:
        *   **Non chiedere** date di cutoff (né per le azioni né per il cash). Procedi direttamente rilevandole automaticamente dal file.
    *   Se **manca**:
        *   Spiega all'utente che può caricare `activity-summary.csv` per rilevare i cutoff in automatico (mostra *Istruzioni activity-summary.csv*).
        *   Se l'utente preferisce non caricarlo, **devi chiedere manualmente**:
            1. *"Ci sono stati momenti in cui hai venduto o trasferito tutte le azioni dal conto? Se sì, indicami le date (cutoff)."*
            2. *"Il file delle azioni contiene una colonna 'Sale Date' per le vendite singole?"*

3.  **Raccogli i parametri comuni**:
    *   Chiedi sempre l'**Anno Fiscale** di riferimento se non specificato.

---

#### Istruzioni di Download (da mostrare solo se i file mancano):

*   **Istruzioni `ss.csv` (Azioni):**
    1. Accedi a **Morgan Stanley atWork**.
    2. Clicca su **Activity** > **Reports** > **Your Alphabet Stock Statement**.
    3. Imposta: *Reporting Period* = `All available history`, *Currency* = `USD`, *Output Format* = `CSV`.
    4. Scarica e salva come `ss.csv` nella radice del progetto.

*   **Istruzioni `activity-summary.csv` (Dividendi/Cash/Cutoff):**
    1. Accedi a **Morgan Stanley atWork**.
    2. Vai su **Activity** > **Reports** > **Account Summary**.
    3. Imposta: *Period* = `All Available History`, spunta *Share & Cash Holdings* e *Equity Awards*, *View As* = `Web Page`, *Type* = `Full`.
    4. Clicca su **Submit**. Scorri in fondo, cerca "IRS Nonresident Alien Withholding".
    5. Copia la tabella **Activity** (dall'intestazione alla fine), incollala in Excel/Sheets ed esportala come `activity-summary.csv` nella radice del progetto.

*   **Metodo Alternativo via HTML (Consigliato, evita il copia/incolla):**
    1. Esegui i passaggi da 1 a 3 delle istruzioni per `activity-summary.csv` (impostazione filtri).
    2. **Prima di cliccare su Submit**, apri i *Developer Tools* (F12) e vai sulla tab *Network*.
    3. Clicca su **Submit**.
    4. Nella tab *Network*, individua la richiesta a `userStatement.do` (avvenuta al click di Submit).
    5. Fai click con il tasto destro sulla richiesta e seleziona **Copy** > **Copy as cURL**.
    6. Esegui il comando nel terminale salvando l'output su file (es. aggiungendo `-o account-summary.html` alla fine).
    7. Converti l'HTML in CSV con il parser:
       ```bash
       .venv/bin/python scripts/parse_html_summary.py --html account-summary.html --output account-summary.csv
       ```

### 2. Funzionamento di Cutoffs e Sale Date (Spiegazione all'Utente)
Spiega all'utente come lo script userà le date fornite:
- **Cutoffs Multipli (Stock)**: Lo script li usa per chiudere automaticamente le finestre di possesso delle azioni maturate fino a quel momento.
- **Cutoffs Cash**: Lo script resetta a zero il saldo accumulato da quella data in poi per il calcolo della giacenza media.

### 3. Esecuzione Tecnica (Consigliata tramite `uv`)
> [!NOTE]
> Gli script utilizzano i metadati in linea per le dipendenze. Usa preferibilmente `uv run` per eseguire gli script senza dover configurare manualmente l'ambiente.

Se l'ambiente supporta `uv`, esegui direttamente:

**Esecuzione Calcolo Stock:**
```bash
uv run scripts/calcola_ivafe.py --csv report_azioni.csv --anno 2024 --account-summary account-summary.csv
```

**Esecuzione Calcolo Dividendi e IVAFE Cash:**
```bash
uv run scripts/calcola_dividendi.py --csv account-summary.csv --anno 2024 --cutoff 2024-10-01
```

*(In caso di fallback senza `uv`, crea un virtual environment, installa da `scripts/requirements.txt` ed esegui con `python`)*

## Risultati e Output
Gli script generano tabelle testuali e file CSV (`quadro_rw_...csv` e `quadro_rm_...csv`).

**Obbligo dell'Agente nel presentare i risultati:**
- **Mostra esplicitamente le date di cutoff rilevate e rilevanti** per il calcolo (es. l'ultimo cutoff prima dell'anno fiscale e quelli avvenuti durante l'anno).
- Verifica con l'utente se i risultati riflettono la sua situazione reale prima di considerare il compito concluso.
