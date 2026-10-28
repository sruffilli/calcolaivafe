---
name: calcola-ivafe
description: Skill per calcolare l'IVAFE per le stock, le imposte sui dividendi (Quadro RM) e l'IVAFE sulla liquidità accumulata (Quadro RW).
---

# Calcolo Fiscale Esteri (Quadro W/RW e M/RM) - Skill Locale

Questa skill automatizza il calcolo dell'imposta IVAFE italiana e la generazione delle righe per la dichiarazione dei redditi (Modello 730 o Modello Redditi PF) partendo da estratti conto di broker esteri.

## Struttura della Skill

I file si trovano nella radice del repository:
- `scripts/calcola_ivafe.py`: Lo script per il calcolo dell'IVAFE su azioni (GSUs).
- `scripts/calcola_dividendi.py`: Lo script per il calcolo delle tasse sui dividendi (Quadro RM/M) e IVAFE su cash (Quadro RW/W).
- `scripts/parse_html_summary.py`: Utility per convertire l'HTML dell'Account Summary in CSV.
- `tests/run.sh`: test automatici sui file sample, senza rete.

Le dipendenze (pandas, yfinance, requests, tabulate) sono dichiarate in testa a ogni script (PEP 723): `uv run` le risolve da solo. Gli script scrivono i CSV di output nella directory corrente.

## Documentazione di Riferimento
- [IVAFE.md](../../../references/IVAFE.md): Report sull'architettura normativa dell'IVAFE.
- [DIVIDENDI.md](../../../references/DIVIDENDI.md): Guida al calcolo dei dividendi esteri (Netto Frontiera).

## ⚠️ Regole di Esecuzione e Sandbox (Mandatorie)
1. **Nessuno Script Ad-Hoc**: **Non devi mai scrivere script Python o di altro tipo ad-hoc** per eseguire i calcoli, esportare dati o aggirare limitazioni. Devi utilizzare esclusivamente gli script ufficiali presenti nel repository (`calcola_ivafe.py`, `calcola_dividendi.py`, `parse_html_summary.py`).
2. **Politica Sandbox (Connessione Internet)**: Gli script richiedono l'accesso a Internet per scaricare i tassi di cambio (Banca d'Italia) e le quotazioni (Yahoo Finance). Se un tasso non è recuperabile gli script **terminano con errore** (exit 1) invece di produrre numeri parziali: non interpretare un'uscita con errore come "risultato zero".
   - Se l'ambiente in cui ti trovi (sandbox dell'agente) blocca queste connessioni o se l'utente non riesce ad approvare i comandi di rete, **non provare a creare script offline o a cablare dati manualmente**.
   - **Devi avvisare immediatamente l'utente e fermare l'esecuzione**, spiegando che l'ambiente è limitato (sandboxed) e consigliando all'utente di eseguire gli script localmente sul proprio computer o tramite un agente non sandboxed.

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
        *   Lo script stampa, per ogni cutoff rilevato, il **saldo azioni residuo** dopo il trasferimento. Se una riga è marcata `PARZIALE`, il trasferimento non ha svuotato il conto: **fermati e chiedi all'utente** quali lotti sono stati trasferiti, perché lo script tratta ogni cutoff come liquidazione totale dei lotti maturati fino a quella data. Non rilanciare con cutoff diversi per "far sparire" l'avviso.
    *   Se **manca**:
        *   Spiega all'utente che può caricare `activity-summary.csv` per rilevare i cutoff in automatico (mostra *Istruzioni activity-summary.csv*).
        *   Se l'utente preferisce non caricarlo, **devi chiedere manualmente**:
            1. *"Ci sono stati momenti in cui hai venduto o trasferito tutte le azioni dal conto? Se sì, indicami le date (cutoff)."*
            2. *"Il file delle azioni contiene una colonna 'Sale Date' per le vendite singole?"*

3.  **Raccogli i parametri comuni**:
    *   Chiedi sempre l'**Anno Fiscale** di riferimento se non specificato.
    *   Chiedi all'utente se intende presentare il **Modello 730** (Quadro W e Quadro M) o il **Modello Redditi PF** (Quadro RW e Quadro RM) per adattare la spiegazione dei risultati.

---

#### Istruzioni di Download (da mostrare solo se i file mancano):

> [!WARNING]
> Non suggerire all'utente di fare "Salva con nome..." dal browser per l'Account Summary, perché salverebbe solo lo scheletro JavaScript senza i dati reali. Segui rigorosamente una delle due opzioni sotto.

*   **Istruzioni `ss.csv` (Azioni):**
    1. Accedi a **Morgan Stanley atWork**.
    2. Clicca su **Activity** > **Reports** > **Your Alphabet Stock Statement**.
    3. Imposta: *Reporting Period* = `All available history`, *Currency* = `USD`, *Output Format* = `CSV`.
    4. Scarica e salva come `ss.csv` nella radice del progetto.

*   **Istruzioni `activity-summary.csv` (Dividendi/Cash/Cutoff) - Copia e Incolla:**
    1. Accedi a **Morgan Stanley atWork** > **Activity** > **Reports** > **Account Summary**.
    2. Imposta: *Period* = `All Available History`, spunta *Share & Cash Holdings* e *Equity Awards*, *View As* = `Web Page`, *Type* = `Full`.
    3. Clicca su **Submit**.
    4. Scorri in fondo alla pagina generata, seleziona l'intera tabella **Activity** (dall'intestazione alla fine), copiala e incollala in Excel/Sheets, quindi esportala come `activity-summary.csv` nella radice del progetto.

*   **Metodo Alternativo via HTML (Crea file tramite cURL):**
    1. Esegui i passaggi da 1 a 3 delle istruzioni sopra (impostazione filtri).
    2. **Prima di cliccare su Submit**, apri i *Developer Tools* (F12) e vai sulla tab *Network*.
    3. Clicca su **Submit**.
    4. Nella tab *Network*, individua la richiesta a `userStatement.do` (avvenuta al click di Submit).
    5. Fai click con il tasto destro sulla richiesta e seleziona **Copy** > **Copy as cURL**.
    6. Esegui il comando nel terminale salvando l'output su file (es. aggiungendo `-o account-summary.html` alla fine).
    7. Converti l'HTML in CSV con il parser:
       ```bash
       uv run scripts/parse_html_summary.py --html account-summary.html --output account-summary.csv
       ```

### 2. Esecuzione Tecnica (Consigliata tramite `uv`)
Se l'ambiente supporta `uv` ed ha accesso a Internet, esegui:

**Esecuzione Calcolo Stock:**
```bash
uv run scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --account-summary account-summary.csv
```

**Esecuzione Calcolo Dividendi e IVAFE Cash:**
```bash
uv run scripts/calcola_dividendi.py --csv account-summary.csv --anno 2025
```

## Risultati e Output

Gli script generano tabelle testuali e file CSV. Quando presenti i risultati all'utente, adattali a seconda del modello di dichiarazione scelto:

### A) Modello 730 (Precompilata)
- **Quadro W (ex RW) - Investimenti**: Mostra i dati aggregati riga per riga da inserire nelle colonne 1, 3, 4, 5, 6, 7, 8, 10.
  - *Nota*: **Non c'è la colonna per l'IVAFE calcolata** (Colonna 11 in RW). L'imposta viene calcolata automaticamente dal software 730. 
  - *Nota sui Giorni (Colonna 10)*: Se l'arrotondamento del software genera discrepanze sul totale, consiglia all'utente di inserire i "Giorni Equivalenti/Pesati" calcolati dallo script per far coincidere il calcolo automatico con l'imposta reale pro-rata.
- **Quadro M (ex RM) - Dividendi**: Mostra i dati per compilare il rigo **M31** (Tipo: `H`, Stato: `069`, Reddito: importo **al lordo** delle ritenute estere, Aliquota: `26`). Segnala all'utente che la ritenuta estera può essere recuperata tramite istanza di rimborso (Cassazione 25698/2022 e 10204/2024), non riducendo la base imponibile.

### B) Modello Redditi PF
- **Quadro RW - Investimenti**: Mostra i dati includendo anche la colonna 11 (IVAFE calcolata) e i totali dell'imposta da versare.
- **Quadro RM - Dividendi**: Mostra i dati per la compilazione del rigo **RM31** (Sezione II-A) (Tipo: `H`, Stato: `069`, Reddito: importo **al lordo** delle ritenute estere, Aliquota: `26`, Imposta dovuta). Segnala all'utente che la ritenuta estera può essere recuperata tramite istanza di rimborso (Cassazione 25698/2022 e 10204/2024), non riducendo la base imponibile.

Verifica sempre con l'utente se i risultati riflettono la sua situazione reale prima di considerare il compito concluso.
