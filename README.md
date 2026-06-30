# Calcola IVAFE (Quadro RW e RM)

Questo repository contiene strumenti in Python per il calcolo dell'imposta **IVAFE** (Azioni e Liquidità) e dei dividendi esteri, generando le righe per i quadri **RW** e **RM** della dichiarazione dei redditi italiana.

Progettato originariamente per la gestione di **Google GSUs** (Alphabet Inc.) e conti Morgan Stanley, ma estensibile a qualsiasi titolo estero tracciabile su Yahoo Finance.

---

## 📂 Preparazione Dati: Scaricare i file da Morgan Stanley

Lo strumento richiede due file diversi a seconda del calcolo da effettuare.

### 1. File per Azioni (`ss.csv`)
Per il calcolo IVAFE sulle azioni:
1. Accedi a **Morgan Stanley atWork**.
2. Nel menu superiore, clicca su **Activity** > **Reports** > **Your Alphabet Stock Statement**.
3. Imposta:
   - **Reporting Period**: `All available history`.
   - **Choose a currency**: `USD`.
   - **Output Format**: `CSV`.
4. Clicca su **Run Report**.
5. Scarica il file e rinominalo in `ss.csv` nella radice del progetto.

### 2. File per Dividendi e Cash (`activity-summary.csv` o `account-summary.csv`)
Per il calcolo di dividendi e liquidità:

#### Opzione A: Tramite HTML e Parser (Raccomandato, evita il copia/incolla)
1. Accedi a **Morgan Stanley atWork**.
2. Naviga su **Activity** > **Reports** > **Account Summary**.
3. Imposta:
   - **Period Quick Select**: `All Available History`.
   - **Product Selection**: Spunta sia `Share & Cash Holdings` che `Equity Awards`.
   - **View As**: `Web Page`.
   - **Account Summary Type**: `Full`.
4. **Prima di cliccare su Submit**, apri i *Developer Tools* del browser (F12) e vai sulla tab *Network*.
5. Clicca su **Submit**.
6. Nella tab *Network*, individua la richiesta a `userStatement.do`.
7. Fai click con il tasto destro sulla richiesta e seleziona **Copy** > **Copy as cURL**.
8. Esegui il comando nel terminale salvando l'output su file (es. aggiungendo `-o account-summary.html` alla fine).
9. Converti l'HTML in CSV usando lo script di utility:
   ```bash
   uv run scripts/parse_html_summary.py --html account-summary.html --output activity-summary.csv
   ```

#### Opzione B: Copia e Incolla Manuale
1. Esegui i passaggi da 1 a 4 dell'Opzione A (senza aprire i DevTools).
2. Clicca su **Submit**.
3. Scorri fino in fondo alla tabella **Activity** (Entry Date, Activity, ecc.) nella pagina generata.
4. Copia i dati, incollali in un foglio di calcolo ed esporta in CSV come `activity-summary.csv` nella radice del progetto.

---

## 💻 Utilizzo tramite CLI (Agent-Agnostic)

Puoi eseguire i calcoli manualmente sul tuo computer.

### Requisiti
- [uv](https://github.com/astral-sh/uv) (consigliato, gestisce automaticamente dipendenze e ambienti) o Python 3.10+ con installazione manuale delle dipendenze.

### 🚀 Esecuzione rapida con `uv` (Raccomandato)
Non è necessario creare un virtual environment o installare dipendenze. `uv` si occuperà di tutto in automatico leggendo i metadati all'interno degli script.

**1. Calcolo IVAFE Azioni (Quadro RW):**
```bash
uv run scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --account-summary activity-summary.csv
```
*   **Rilevamento Automatico dei Cutoff**: Lo script rileverà automaticamente le date di trasferimento delle azioni (`Transfer out`) da `activity-summary.csv`.
*   **Cutoff Manuali (Opzionale)**:
    ```bash
    uv run scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --account-summary activity-summary.csv --cutoff 2025-11-20
    ```

**2. Calcolo Dividendi e IVAFE Cassa (Quadri RM e RW):**
```bash
uv run scripts/calcola_dividendi.py --csv activity-summary.csv --anno 2025
```

---

### 🐍 Esecuzione classica con Python (Alternativa)
Se non utilizzi `uv`, puoi procedere nel modo classico:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --index-url https://pypi.org/simple -r scripts/requirements.txt
python scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --account-summary activity-summary.csv
python scripts/calcola_dividendi.py --csv activity-summary.csv --anno 2025
```

---

## 🤖 Utilizzo con Agenti AI

### Con Antigravity (o `antigravity-cli`)
Questo repository è configurato come una **Skill locale** per Antigravity. 
Se usi `antigravity-cli` in questa cartella, l'agente rileverà automaticamente la skill.

**Esempi di comandi:**
- `@antigravity calcola le tasse per l'anno 2025`
- `@antigravity esegui calcola-ivafe per il 2025 con cutoff 2025-11-20`

L'agente leggerà le istruzioni in `.agents/skills/calcola-ivafe/SKILL.md`, ti guiderà nell'intervista iniziale e lancerà gli script per te.

### Con altri Agenti (ChatGPT, Claude, ecc.)
Puoi usare questi script con qualsiasi altro LLM (es. caricando i file in un "Project" di Claude o in una chat di ChatGPT Plus):
1.  Carica i file `scripts/calcola_ivafe.py` e `scripts/calcola_dividendi.py`.
2.  Carica i tuoi file di dati (`ss.csv` e/o `activity-summary.csv`).
3.  Carica i file in `references/` per dare all'agente il contesto normativo italiano.
4.  Usa un prompt del tipo:
    > *"Usa gli script python forniti per calcolare l'IVAFE/dividendi per l'anno [ANNO]. I miei dati sono in [FILE]. Se hai bisogno di chiarimenti su date di cutoff o vendite, chiedimi prima di procedere."*

---

## Riferimenti Normativi
I dettagli sul calcolo e le circolari dell'Agenzia delle Entrate sono documentati in:
- [IVAFE.md](references/IVAFE.md)
- [DIVIDENDI.md](references/DIVIDENDI.md)

## Disclaimer
Questo strumento è un ausilio al calcolo e non sostituisce il parere di un consulente fiscale.
