# Calcola IVAFE — Skill per Gemini (Quadro RW e RM)

Questo repository contiene **una Skill per Gemini** (disponibile nella cartella `.gemini/skills/calcola-ivafe/`). Consente a un assistente AI abilitato di guidarti ed eseguire automaticamente il calcolo dell'imposta **IVAFE** (Azioni e Liquidità) e dei dividendi esteri, generando le righe per i quadri **RW** e **RM** della dichiarazione dei redditi italiana.

Progettato specificamente per la gestione di **Google GSUs** (Alphabet Inc.) e conti Morgan Stanley, ma estensibile a qualsiasi titolo estero tracciabile su Yahoo Finance.

## 🤖 Come usare la Skill con Gemini (Metodo Principale)

Se stai usando un ambiente compatibile con le skill di Gemini (come questo), puoi invocare la skill semplicemente chiedendo all'assistente di eseguire il calcolo.

**Esempio di invocazione:**
- *"Usa la skill `calcola-ivafe` per calcolare i quadri RW e RM per l'anno 2024, con una data di cutoff per le azioni del 2024-11-20"*

L'assistente leggerà le istruzioni in `SKILL.md` e ti guiderà passo passo, chiedendoti i parametri necessari e i file di input. Se non sai come ottenere i file da Morgan Stanley, consulta la sezione successiva.

## 📈 Caratteristiche Principali

- 📊 **Integrazione API**: Recupero automatico dei prezzi storici tramite `yfinance` e dei tassi di cambio ufficiali (USD/EUR) tramite le API di **Banca d'Italia**.
- 🔄 **Rolling Cutoff Strategy**: Supporto per la gestione di liquidazioni totali in date multiple.
- 📂 **Parsing Dinamico**: Supporta il formato CSV di Morgan Stanley e vendite singole.
- 📋 **Quadro RW e RM Ready**: Genera file CSV aggregati per i quadri RW (Azioni e Cash) e RM (Dividendi).
- 💰 **Dividendi e Cash**: Calcolo del "Netto Frontiera" e della giacenza media della liquidità.
- ⚡ **Cache In-Memory**: Ottimizzato per evitare chiamate API ridondanti.

---

## 📂 Preparazione Dati: Scaricare i file da Morgan Stanley

Lo strumento richiede due file diversi a seconda del calcolo da effettuare. **Nota: Il recupero di questi file è un passo preliminare obbligatorio sia per l'utilizzo tramite Skill Gemini che per l'uso manuale degli script.**

#### 1. File per Azioni (ss.csv)
Per lo script `calcola_ivafe.py`:
1. Accedi a **Morgan Stanley atWork** (es. tramite il link `go/mssb` se disponibile, o direttamente su `https://atwork.morganstanley.com`).
2. Nel menu superiore, clicca su **Activity** > **Your Alphabet Stock Statement**.
3. Imposta:
   - **Reporting Period**: `All available history`.
   - **Choose a currency**: `USD`.
   - **Output Format**: `CSV`.
4. Clicca su **Run Report**.
5. Scarica il file tramite il link `"Please click here to download"` e rinominalo in `ss.csv`.

#### 2. File per Dividendi e Cash (activity-summary.csv)
Per lo script `calcola_dividendi.py`:
1. Accedi a **Morgan Stanley atWork**.
2. Nel menu superiore, naviga su **Activity** > **Reports** > **Account Summary**.
3. Nella pagina di configurazione, imposta:
   - **Period Quick Select**: `All Available History` (o seleziona il periodo desiderato).
   - **Product Selection**: Spunta sia `Share & Cash Holdings` che `Equity Awards`.
   - **View As**: Seleziona `Web Page`.
   - **Account Summary Type**: Seleziona `Full`.
4. Clicca su **Submit** e attendi la generazione (può richiedere un minuto).
5. Scorri fino in fondo alla pagina (un trucco veloce è cercare con CTRL+F la stringa `"IRS Nonresident Alien Withholding"`).
6. Seleziona e copia tutta la tabella intitolata **Activity** (quella con colonne: *Entry Date, Activity, Type of Money, Cash, Number of Shares*, ecc.) partendo dalla riga di intestazione fino alla fine.
7. Incolla i dati in un foglio di calcolo (es. Google Sheets).
8. Esporta il foglio in formato **CSV** e salvalo come `activity-summary.csv` nella cartella del progetto.

---

## 🐍 Utilizzo alternativo tramite Script Python (Opzionale)

Se preferisci eseguire i calcoli manualmente senza l'ausilio dell'AI, puoi utilizzare direttamente gli script Python presenti nel repository.

### Requisiti per uso manuale
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (consigliato)

### Configurazione Ambiente
```bash
uv venv
source .venv/bin/activate
uv pip install -r .gemini/skills/calcola-ivafe/scripts/requirements.txt
```



### 1. Calcolo IVAFE Azioni (Quadro RW)

Il comando base richiede il file CSV delle azioni e l'anno fiscale:

```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv ss.csv --anno 2025
```

#### Funzionalità Avanzate

**Rolling Cutoffs (Liquidazioni Totali)**
Se durante l'anno (o in quelli passati) hai venduto o trasferito **tutte** le azioni presenti nel conto, puoi usare il parametro `--cutoff`. Lo script supporta date multiple.

```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --cutoff 2024-11-24 2025-06-30
```

**Colonna 'Sale Date' (Vendite Singole)**
Se il tuo file include una colonna intitolata `Sale Date` o `Data Vendita`, lo script userà quella data come termine del possesso.

### 2. Calcolo Dividendi e IVAFE Cassa (Quadri RM e RW)

Il comando richiede il file riepilogativo del conto (`activity-summary.csv`) e l'anno fiscale:

```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_dividendi.py --csv activity-summary.csv --anno 2025
```

### Parametri Comuni e Specifici
- `--csv`: Percorso del file estratto conto (CSV o TSV).
- `--anno`: Anno fiscale di riferimento (default: anno precedente).
- `--cutoff`: 
  - Per `calcola_ivafe.py`: Una o più date di liquidazione totale.
  - Per `calcola_dividendi.py`: Data di azzeramento del conto cash.
- `--ticker`: (Solo per `calcola_ivafe.py`) Ticker Yahoo Finance (default: `GOOG`).

## Riferimenti Normativi e Razionale di Calcolo

Il calcolo dell'IVAFE implementato in questo script segue le direttive dell'Agenzia delle Entrate e le istruzioni del Quadro RW:

### Riferimenti Normativi
- **Circolare n. 28/E del 2 luglio 2012**: Linee guida generali per l'applicazione dell'IVAFE.
- **Circolare n. 10/E del 14 maggio 2014 (Quesito 13.4)**: Specifica che per le attività finanziarie detenute alla data del 1° gennaio si deve utilizzare il cambio medio del mese di dicembre dell'anno precedente.
- **Istruzioni Modello Redditi (Quadro RW)**: Disciplinano la valorizzazione delle attività al valore di mercato (codice 1) e indicano di utilizzare il valore al primo giorno di detenzione per i nuovi acquisti.
- **[DIVIDENDI.md](file:///Users/sruffilli/git/calcolaivafe/.gemini/skills/calcola-ivafe/references/DIVIDENDI.md)**: Documentazione specifica per il calcolo dei dividendi esteri (Netto Frontiera) e Quadro RM.

### Razionale di Calcolo
- **Valore Iniziale**: Per le azioni già possedute al 1° gennaio, viene calcolato usando il prezzo a inizio anno e il tasso di cambio medio di dicembre dell'anno precedente. Per le azioni maturate in corso d'anno (vesting), si usa il valore alla data di maturazione.
- **Valore Finale**: Calcolato al 31 dicembre o alla data di vendita, usando il tasso di cambio medio del mese di riferimento.
- **Proporzionalità**: L'imposta è calcolata pro-rata sui giorni di effettivo possesso. Come da esempi delle istruzioni ministeriali, il denominatore è fissato a **365** giorni anche per gli anni bisestili.
- **Aliquota**: Fissata allo **0.2%** (2 per mille) per i titoli detenuti in paesi White List (come gli USA per le azioni Alphabet).

## Privacy
Lo script è configurato per ignorare i file `*.csv` tramite `.gitignore`. Viene fornito un file `ss.csv.sample` come riferimento per la struttura dei dati.

## Disclaimer
Questo strumento è un ausilio al calcolo e non sostituisce il parere di un consulente fiscale professionista. L'autore non si assume responsabilità per eventuali errori nei dati forniti dalle API esterne o per l'uso improprio dei risultati.
