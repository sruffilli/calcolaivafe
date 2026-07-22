# Guida al Calcolo dell'IVAFE sui Titoli Esteri

Questo documento sintetizza le regole operative per il calcolo dell'Imposta sul Valore delle Attività Finanziarie detenute all'Estero (IVAFE) applicata ai conti titoli e dossier finanziari, con i relativi riferimenti normativi.

## 1. Presupposto Oggettivo e Ambito di Applicazione
L'IVAFE si applica sul valore delle attività finanziarie detenute all'estero da soggetti fiscalmente residenti in Italia (istituita dall'articolo 19, commi da 18 a 22, del D.L. 201/2011). 

Per i **conti titoli** (dossier di custodia e amministrazione), l'imposta segue un binario proporzionale (a differenza dei conti correnti che scontano un'imposta fissa). L'IVAFE si applica sul valore dei singoli asset allocati nel contenitore, quali azioni, obbligazioni e quote di OICR (ETF, fondi). *Nota*: le cripto-attività non sono soggette a IVAFE in senso stretto, ma dal 2023 a un'imposta autonoma sul valore delle cripto-attività (0,2%, codice tributo 1727) con regole analoghe.

*Riferimento principale:* [Circolare n. 28/E del 2 luglio 2012](https://www.agenziaentrate.gov.it/portale/documents/20143/299482/Circolare+28+020712_Cir02.07.12.pdf/27add329-de7a-bbff-135e-c3baf715c7a6).

## 2. Aliquote e Geografia Fiscale
L'ammontare del prelievo dipende dalla giurisdizione in cui l'asset è detenuto o emesso:
- **Aliquota Ordinaria (0,2%)**: Si applica alle attività detenute in paesi collaborativi (White List).
- **Aliquota Raddoppiata (0,4%)**: Si applica ai prodotti finanziari detenuti in Stati o territori a regime fiscale privilegiato, individuati dal **D.M. 4 maggio 1999**.

## 3. Metrica del Valore (Criterio Gerarchico)
Per la definizione della base imponibile degli strumenti finanziari si segue un ordine di priorità inderogabile:
1. **Valore di Mercato (Codice 1)**: Rilevato al termine dell'anno solare (31 dicembre) o al termine del periodo di detenzione.
2. **Valore Nominale (Codice 2)**: In mancanza di quotazione.
3. **Valore di Rimborso (Codice 3)**: In via ulteriormente subordinata.
4. **Costo di Acquisto (Codice 4)**: Se mancano i requisiti precedenti.

## 4. Gestione del Cambio Valutario (Exchange Rates)
Per tradurre in euro i valori espressi in valuta estera, si applicano tassi di conversione rigidi:
- **Valore Iniziale**: Per le attività detenute al 1° gennaio, si deve applicare il tasso di cambio medio del **mese di dicembre dell'anno antecedente**. Per i nuovi acquisti in corso d'anno, si usa il cambio medio del mese di acquisizione.
- **Valore Finale**: Si converte adottando il tasso di cambio medio del mese di dicembre dell'anno di riferimento (o del mese di estinzione dell'attività).

*Riferimento per il cambio iniziale:* [Circolare n. 10/E del 14 maggio 2014](https://def.finanze.it/DocTribFrontend/getContent.do?id=%7B7FE874EE-0753-4D15-B92A-3B7B2153DE55%7D) (Quesito 13.4).

## 5. Algoritmo di Calcolo
L'imposta è calcolata proporzionalmente ai giorni di effettiva detenzione e alla quota di possesso:

$$\text{IVAFE} = \text{Base Imponibile in Euro} \times \text{Aliquota (0,2\% o 0,4\%)} \times \left( \frac{\text{Giorni di Possesso}}{365} \right) \times \text{Quota \%}$$

*Nota sul denominatore:* Gli esempi delle istruzioni ministeriali utilizzano il rapporto su base **365 giorni** anche per gli anni bisestili.

## 6. Mappatura per la Compilazione
A seconda della dichiarazione utilizzata, i dati vanno riportati nel Quadro RW (Modello Redditi) o nel Quadro W (Modello 730).

### A) Modello Redditi PF — Quadro RW
La compilazione pratica segue le istruzioni del [Fascicolo 2 dell'Agenzia delle Entrate (Istruzioni 2026)](https://www.agenziaentrate.gov.it/portale/documents/d/guest/pf2_istruzioni_2026):
- **Colonna 1 (Titolo possesso)**: Codice possesso (es. `1` per proprietà).
- **Colonna 2 (Tipo contribuente)**: *Lasciare vuoto* se proprietario diretto (si compila come `1` per soggetti delegati al prelievo/movimentazione, o `2` per titolari effettivi). I codici sono identici a quelli del Quadro W del Modello 730.
- **Colonna 3 (Codice bene)**: Codice bene (es. `2` per titoli esteri).
- **Colonna 4 (Stato estero)**: Codice Stato (es. `069` per USA).
- **Colonna 5 (Quota possesso)**: Quota % (es. `100`).
- **Colonna 6 (Criterio valore)**: Criterio valore (es. `1` per valore di mercato).
- **Colonna 7 (Valore iniziale)**: Valore all'inizio del periodo d'imposta o al primo giorno di detenzione.
- **Colonna 8 (Valore finale)**: Valore al termine del periodo d'imposta o di detenzione.
- **Colonna 10 (Giorni)**: Numero di giorni di detenzione (rapportati a 365).
- **Colonna 11 (IVAFE Calcolata)**: Risultato dell'applicazione dell'aliquota sul valore finale rapportato ai giorni e alla quota.

### B) Modello 730 — Quadro W (Precompilata)
Il Quadro W riproduce sostanzialmente il Quadro RW, ma con alcune importanti differenze nell'ordine e nella presenza delle colonne (non c'è il calcolo dell'imposta dovuta, effettuato dal software 730):
- **Colonna 1 (Codice titolo possesso)**: `1` (Proprietà)
- **Colonna 2 (Tipo contribuente)**: *Lasciare vuoto* se proprietario diretto (si compila come `1` per soggetti delegati al prelievo/movimentazione, o `2` per titolari effettivi). I codici sono identici a quelli del Quadro RW del Modello Redditi.
- **Colonna 3 (Codice individuazione bene)**: `2` (Titoli esteri)
- **Colonna 4 (Codice Stato estero)**: `069` (Stati Uniti)
- **Colonna 5 (Quota di possesso)**: `100` (%)
- **Colonna 6 (Criterio determinazione valore)**: `1` (Valore di mercato)
- **Colonna 7 (Valore iniziale)**: Valore iniziale in Euro.
- **Colonna 8 (Valore finale)**: Valore finale in Euro.
- **Colonna 10 (Giorni IVAFE - Cripto-attività)**: Giorni di possesso.
  - *Nota*: **Manca la colonna "IVAFE Calcolata"**. L'imposta viene liquidata nel foglio di sintesi `730-3`. 
  - *Nota sui Giorni Equivalenti*: Poiché il software del 730 calcola l'imposta in modo rigido sul valore finale aggregato, per evitare che applichi 365 giorni su lotti detenuti solo in parte, occorre inserire i "Giorni Equivalenti" calcolati dallo script nel campo dei giorni per far quadrare l'arrotondamento con l'imposta reale pro-rata.

## 7. Nota sui Redditi di Capitale (Dividendi)
L'IVAFE è un'imposta patrimoniale che si applica sul valore delle attività finanziarie detenute all'estero (lo *stock* di capitale). I proventi derivanti da tali attività, come i **dividendi**, costituiscono invece redditi di capitale e non sono soggetti a IVAFE in sé.
- I dividendi vanno dichiarati nel **Quadro RM** (Modello Redditi, rigo RM31) o nel **Quadro M** (Modello 730, rigo M31) e tassati con imposta sostitutiva del 26% sull'importo **al lordo** delle ritenute estere (vedi [DIVIDENDI.md](DIVIDENDI.md) per il dibattito lordo/netto frontiera e il rimedio del credito d'imposta secondo la Cassazione).
- Tuttavia, se i dividendi percepiti vengono mantenuti sul conto corrente estero, essi concorrono a formare la giacenza del conto stesso. Se la giacenza media supera i 5.000 euro, il conto sarà soggetto all'IVAFE fissa di 34,20 euro (come descritto nella Deroga Bancaria).