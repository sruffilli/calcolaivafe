# Guida al Calcolo e alla Dichiarazione dei Dividendi Esteri (Quadro RM)

Questo documento sintetizza le regole operative per la tassazione dei dividendi percepiti da fonti estere (senza intermediario italiano) e la loro indicazione nel Quadro RM del Modello Redditi, con i relativi riferimenti normativi e giurisprudenziali.

## 1. Presupposto e Tassazione
I dividendi percepiti da persone fisiche residenti in Italia e derivanti da partecipazioni in società estere si qualificano come **redditi di capitale** (Art. 44 del TUIR).

In assenza di un intermediario residente (es. broker italiano) che applichi la ritenuta alla fonte, il contribuente deve liquidare l'imposta in autoliquidazione. L'aliquota ordinaria è fissata al **26%** (Art. 27, comma 4 e 4-bis, del D.P.R. n. 600/1973).

## 2. Il Principio del "Netto Frontiera"
Storicamente, l'Agenzia delle Entrate richiedeva di calcolare il 26% sull'importo *lordo* del dividendo (prima delle ritenute dello Stato estero), generando una doppia imposizione.

La Corte di Cassazione ha definitivamente ribaltato questo approccio con due pronunce storiche:
- **[Ordinanza n. 25698 del 1° settembre 2022](https://def.finanze.it/DocTribFrontend/getGiurisprudenzaDetail.do?id=%7B38723DA3-AFB8-4CFF-A7DC-0D3FB5841DB1%7D)**
- **[Ordinanza n. 10204 del 16 aprile 2024](https://www.studiocerbone.com/corte-di-cassazione-sezione-tributaria-sentenza-n-10204-depositata-il-16-aprile-2024-limposta-sostitutiva-prevista-dallart-18-del-d-p-r-n-917-del-1986-ha-una-funzione-del-tutto-sovrapponib/)**

I principi cardine stabiliti sono:
1. **Identità di Funzione**: L'imposta sostitutiva calcolata dal contribuente ha la stessa funzione della ritenuta operata dall'intermediario italiano.
2. **Netto Frontiera**: La base imponibile su cui applicare il 26% è l'importo che effettivamente "attraversa la frontiera", ovvero il dividendo **al netto della ritenuta subita all'estero** (es. il 15% per i dividendi USA).
3. **Prevalenza del Diritto Convenzionale**: Le Convenzioni contro le doppie imposizioni prevalgono sulle norme interne restrittive.

### Esempio di Calcolo (Netto Frontiera):
- Dividendo Lordo: € 1.000,00
- Ritenuta Estera (es. USA 15%): € 150,00
- **Importo Netto Incassato (Netto Frontiera)**: € 850,00
- **Imposta Italiana (26% su € 850)**: € 221,00
- Netto Finale per l'Investitore: € 629,00 (invece di € 590,00 calcolati sul lordo).

## 3. Mappatura per la Compilazione
A seconda della dichiarazione utilizzata, i proventi vanno dichiarati nel Quadro RM (Modello Redditi) o nel Quadro M (Modello 730).

### A) Modello Redditi PF — Sezione V del Quadro RM
- **Tipo di Reddito**: Codice identificativo per i dividendi esteri (es. `H` o `I` a seconda del caso).
- **Base Imponibile**: Inserire il valore del **Netto Frontiera** (importo accreditato).
- **Aliquota**: 26%.

### B) Modello 730 — Rigo M31 del Quadro M (Precompilata)
Nel 730 precompilato, i dividendi esteri confluiscono nel Quadro M, rigo M31:
- **Colonna 1 (Tipo)**: `H` (Utili e altri proventi da partecipazioni estere).
- **Colonna 2 (Codice Stato estero)**: `069` (Stati Uniti).
- **Colonna 3 (Ammontare reddito)**: Inserire l'importo del **Netto Frontiera** convertito in Euro (al netto delle ritenute estere del 15%).
- **Colonna 4 (Aliquota %)**: `26` (%).
- *Nota*: L'imposta sostitutiva del 26% viene calcolata automaticamente dal software 730 nel riepilogo `730-3`.

*Nota sulle Minusvalenze:* La tassazione dei dividendi è isolata. I redditi di capitale **non ammettono** la compensazione con minusvalenze finanziarie (le quali appartengono ai redditi diversi del Quadro RT/T).

## 4. Rapporto con altri Quadri (RT/T e RW/W)
- **Quadro RT / Quadro T (Plusvalenze)**: Si applicano alle plusvalenze/minusvalenze da compravendita (capital gains), non alla percezione di dividendi.
- **Quadro RW / Quadro W (IVAFE)**: L'IVAFE si applica al valore patrimoniale dell'asset (le azioni possedute). Il dividendo in sé è un reddito. Se i dividendi rimangono sul conto estero, concorrono alla giacenza media per la verifica del superamento dei 5.000€ (IVAFE sul cash).
