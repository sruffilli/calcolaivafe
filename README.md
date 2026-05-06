# Calcola IVAFE — Automazione Quadro RW

Strumento Python per il calcolo automatico dell'imposta **IVAFE** e la generazione delle righe per il **Quadro RW** della dichiarazione dei redditi italiana. 

Progettato specificamente per la gestione di **Google GSUs** (Alphabet Inc.), ma estensibile a qualsiasi titolo estero tracciabile su Yahoo Finance.

## Caratteristiche Principali

- 📈 **Integrazione API**: Recupero automatico dei prezzi storici tramite `yfinance` e dei tassi di cambio ufficiali (USD/EUR) tramite le API di **Banca d'Italia**.
- 🔄 **Rolling Cutoff Strategy**: Supporto per la gestione di liquidazioni totali in date multiple. Utile se vendi tutto e ricominci ad accumulare, permettendo di calcolare i giorni di possesso effettivi.
- 📂 **Parsing Dinamico**: Supporta il formato CSV di Morgan Stanley e permette di specificare date di vendita (`Sale Date`) riga per riga.
- 📋 **Quadro RW Ready**: Genera un file CSV aggregato secondo i criteri richiesti dal Quadro RW (aggregazione per date e codici stato).
- ⚡ **Cache In-Memory**: Ottimizzato per evitare chiamate API ridondanti durante l'elaborazione di grandi dataset.

## Requisiti

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (consigliato per la gestione rapida del venv)

## Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/sruffilli/calcolaivafe.git
   cd calcolaivafe
   ```

2. Configura l'ambiente:
   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r .gemini/skills/calcola-ivafe/scripts/requirements.txt
   ```

## Utilizzo

Il comando base richiede il file CSV e l'anno fiscale:

```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv ss.csv --anno 2025
```

### Funzionalità Avanzate

#### Rolling Cutoffs (Liquidazioni Totali)
Se durante l'anno (o in quelli passati) hai venduto o trasferito **tutte** le azioni presenti nel conto, puoi usare il parametro `--cutoff`. Lo script supporta date multiple.
Ogni azione viene assegnata al **primo cutoff** che si verifica alla data di maturazione o dopo di essa. Questo simula uno svuotamento periodico del conto.

```bash
python .gemini/skills/calcola-ivafe/scripts/calcola_ivafe.py --csv ss.csv --anno 2025 --cutoff 2024-11-24 2025-06-30
```

#### Colonna 'Sale Date' (Vendite Singole)
Se il tuo file (CSV o TSV) include una colonna intitolata `Sale Date` o `Data Vendita`, lo script userà quella data specifica come termine del possesso per quella riga. La data di vendita prevale sulla fine dell'anno se precedente. Questo permette una precisione millimetrica per vendite di singoli blocchi.

### Parametri
- `--csv`: Percorso del file estratto conto (supporta sia CSV che TSV).
- `--anno`: Anno fiscale di riferimento (default: anno precedente).
- `--cutoff`: Una o più date (YYYY-MM-DD) di liquidazione totale.
- `--ticker`: Ticker Yahoo Finance (default: `GOOG`).

## Privacy
Lo script è configurato per ignorare i file `*.csv` tramite `.gitignore`. Viene fornito un file `ss.csv.sample` come riferimento per la struttura dei dati.

## Disclaimer
Questo strumento è un ausilio al calcolo e non sostituisce il parere di un consulente fiscale professionista. L'autore non si assume responsabilità per eventuali errori nei dati forniti dalle API esterne o per l'uso improprio dei risultati.
