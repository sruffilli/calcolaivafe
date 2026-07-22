# Guida al Calcolo e alla Dichiarazione dei Dividendi Esteri (Rigo RM31 / M31)

Questo documento sintetizza le regole operative per la tassazione dei dividendi percepiti da fonti estere (senza intermediario italiano) e la loro indicazione nella dichiarazione dei redditi, con i relativi riferimenti normativi e giurisprudenziali.

## 1. Presupposto e Tassazione
I dividendi percepiti da persone fisiche residenti in Italia e derivanti da partecipazioni in società estere si qualificano come **redditi di capitale** (Art. 44 del TUIR).

In assenza di un intermediario residente (es. broker italiano) che applichi la ritenuta alla fonte, il contribuente deve liquidare l'imposta in autoliquidazione tramite imposta sostitutiva (Art. 18 del TUIR), nella stessa misura della ritenuta a titolo d'imposta applicata in Italia sui redditi della stessa natura: **26%** (Art. 27, comma 4 e 4-bis, del D.P.R. n. 600/1973). Per gli utili di fonte estera (codice `H`) **non è possibile optare per la tassazione ordinaria**.

## 2. Base Imponibile: "Lordo Frontiera" vs "Netto Frontiera"

### Posizione ufficiale (istruzioni ministeriali): LORDO
Le istruzioni al Modello Redditi PF (rigo RM31) e al Modello 730 (rigo M31) richiedono testualmente di indicare *"l'ammontare del reddito, **al lordo** di eventuali ritenute subìte nello Stato estero in cui il reddito è stato prodotto"*. Questa è la posizione costante dell'Agenzia delle Entrate per i dividendi percepiti **senza** intermediario residente: la base imponibile del 26% è il dividendo lordo (c.d. "lordo frontiera"). Il principio del "netto frontiera" (Art. 27, comma 4, D.P.R. 600/1973) si applica per legge solo quando interviene un intermediario residente che opera la ritenuta d'ingresso.

### Giurisprudenza di Cassazione: credito d'imposta / rimborso (non riduzione della base)
La Corte di Cassazione si è pronunciata sulla doppia imposizione con due pronunce rilevanti:
- **[Sentenza n. 25698 del 1° settembre 2022](https://def.finanze.it/DocTribFrontend/getGiurisprudenzaDetail.do?id=%7B38723DA3-AFB8-4CFF-A7DC-0D3FB5841DB1%7D)**
- **[Sentenza n. 10204 del 16 aprile 2024](https://www.studiocerbone.com/corte-di-cassazione-sezione-tributaria-sentenza-n-10204-depositata-il-16-aprile-2024-limposta-sostitutiva-prevista-dallart-18-del-d-p-r-n-917-del-1986-ha-una-funzione-del-tutto-sovrapponib/)**

> [!IMPORTANT]
> Contrariamente a una lettura diffusa, queste pronunce **non** legittimano la dichiarazione della base imponibile al netto della ritenuta estera. Esse riconoscono invece il **credito per le imposte pagate all'estero** (Art. 165 TUIR, in forza delle Convenzioni contro le doppie imposizioni): quando l'imposta sostitutiva è applicata obbligatoriamente (e non su richiesta del contribuente), la Convenzione prevale sulla norma interna che nega il credito. Il rimedio operativo è lo scomputo/rimborso della ritenuta estera, non la riduzione della base imponibile.

### Confronto numerico (dividendo USA, ritenuta convenzionale 15%)
- Dividendo Lordo: € 1.000,00 — Ritenuta Estera: € 150,00

| Approccio | Imposta italiana | Carico totale (estero + Italia) | Note |
|---|---|---|---|
| **Lordo, senza credito** (posizione AdE) | 26% × 1.000 = € 260 | € 410 | Conforme alle istruzioni; doppia imposizione |
| **Lordo + credito/rimborso** (Cassazione) | € 260 − 150 = € 110 | € 260 | Lordo in dichiarazione + istanza di rimborso della ritenuta estera |
| **Netto frontiera** (26% × 850 = € 221) | € 221 | € 371 | **Non conforme alle istruzioni**: posizione contestabile in accertamento |

### Approccio consigliato (prudente)
1. Dichiarare il dividendo **al lordo** della ritenuta estera (conforme alle istruzioni RM31/M31) e versare il 26% sul lordo.
2. Presentare **istanza di rimborso** all'Agenzia delle Entrate per la ritenuta estera, fondata sulla giurisprudenza di Cassazione citata (ed eventualmente ricorrere avverso il diniego).

Chi sceglie di dichiarare il netto frontiera deve essere consapevole che si tratta di una posizione difforme dalle istruzioni ufficiali, con rischio di accertamento e sanzioni.

### Tasso di Cambio per i Dividendi
La conversione in Euro dei dividendi espressi in valuta estera (es. USD) deve avvenire applicando il **cambio del giorno in cui i proventi sono percepiti** (data di accredito), ai sensi dell'**Art. 9, comma 2, del TUIR** (cfr. anche Risoluzione n. 57/E del 2016). In pratica si utilizza il tasso di cambio giornaliero della Banca d'Italia riferito alla data di effettivo incasso.

Non si deve utilizzare il tasso medio mensile, che è invece riservato per le valorizzazioni patrimoniali del Quadro RW (IVAFE).

## 3. Mappatura per la Compilazione
A seconda della dichiarazione utilizzata, i proventi vanno dichiarati nel Quadro RM (Modello Redditi) o nel Quadro M (Modello 730). Nei modelli più recenti la sezione dedicata ai redditi di capitale di fonte estera soggetti a imposizione sostitutiva è il **rigo RM31 (Sezione II-A)** del Quadro RM, rinumerato per allinearsi al rigo M31 del 730 (nei modelli meno recenti era la "Sezione V").

### A) Modello Redditi PF — Rigo RM31 (Sezione II-A) del Quadro RM
- **Colonna 1 (Tipo di Reddito)**: `H` (utili di fonte estera assoggettati a ritenuta a titolo d'imposta del 26%). Il codice `I` è residuale ("altri redditi di capitale di fonte estera") e non è quello tipico dei dividendi.
- **Colonna 2 (Codice Stato estero)**: `069` (Stati Uniti).
- **Colonna 3 (Ammontare reddito)**: importo **al lordo** delle ritenute estere, convertito in Euro.
- **Colonna 4 (Aliquota)**: 26%.
- **Imposta dovuta**: nella colonna dedicata.

### B) Modello 730 — Rigo M31 del Quadro M (Precompilata)
Nel 730, i dividendi esteri confluiscono nel Quadro M, rigo M31:
- **Colonna 1 (Tipo)**: `H` (Utili e altri proventi da partecipazioni estere).
- **Colonna 2 (Codice Stato estero)**: `069` (Stati Uniti).
- **Colonna 3 (Ammontare reddito)**: importo **al lordo** delle ritenute estere, convertito in Euro.
- **Colonna 4 (Aliquota %)**: `26` (%).
- *Nota*: L'imposta sostitutiva del 26% viene calcolata automaticamente dal software 730 nel riepilogo `730-3`.

*Nota sulle Minusvalenze:* La tassazione dei dividendi è isolata. I redditi di capitale **non ammettono** la compensazione con minusvalenze finanziarie (le quali appartengono ai redditi diversi del Quadro RT/T).

## 4. Rapporto con altri Quadri (RT/T e RW/W)
- **Quadro RT / Quadro T (Plusvalenze)**: Si applicano alle plusvalenze/minusvalenze da compravendita (capital gains), non alla percezione di dividendi.
- **Quadro RW / Quadro W (IVAFE)**: L'IVAFE si applica al valore patrimoniale dell'asset (le azioni possedute). Il dividendo in sé è un reddito. Se i dividendi rimangono sul conto estero, concorrono alla giacenza media per la verifica del superamento dei 5.000€ (IVAFE sul cash).
