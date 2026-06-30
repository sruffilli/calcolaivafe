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

### 2. File per Dividendi e Cash (`activity-summary.csv`)
Per il calcolo di dividendi e liquidità:
1. Accedi a **Morgan Stanley atWork**.
2. Naviga su **Activity** > **Reports** > **Account Summary**.
3. Imposta:
   - **Period Quick Select**: `All Available History`.
   - **Product Selection**: Spunta sia `Share & Cash Holdings` che `Equity Awards`.
   - **View As**: `Web Page`.
   - **Account Summary Type**: `Full`.
4. Clicca su **Submit**.
5. Scorri fino in fondo alla tabella **Activity** (Entry Date, Activity, ecc.).
6. Copia i dati, incollali in un foglio di calcolo ed esporta in CSV come `activity-summary.csv` nella radice del progetto.

---

## 💻 Utilizzo tramite CLI (Agent-Agnostic)

Puoi eseguire i calcoli manualmente sul tuo computer.

### Requisiti
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (consigliato per la gestione rapida delle dipendenze)

### Configurazione Ambiente
```bash
uv venv
source .venv/bin/activate
uv pip install -r scripts/requirements.txt
```

### 1. Calcolo IVAFE Azioni (Quadro RW)
```bash
python scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --account-summary activity-summary.csv
```
*   **Rilevamento Automatico dei Cutoff**: Passando `--account-summary`, lo script rileverà automaticamente le date di trasferimento delle azioni (attività `Transfer out`) e le userà come cutoff.
*   **Cutoff Manuali (Opzionale)**: Puoi comunque forzare ulteriori date di cutoff manualmente:
    ```bash
    python scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --account-summary activity-summary.csv --cutoff 2025-11-20
    ```

### 2. Calcolo Dividendi e IVAFE Cassa (Quadri RM e RW)
```bash
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
- [IVAFE.md](file:///Users/sruffilli/git/calcolaivafe/references/IVAFE.md)
- [DIVIDENDI.md](file:///Users/sruffilli/git/calcolaivafe/references/DIVIDENDI.md)

## Disclaimer
Questo strumento è un ausilio al calcolo e non sostituisce il parere di un consulente fiscale.
