# TO DO LIST

## Principale
1. FATTO - Fare uno script orchestratore che gestisce tutti gli altri
2. FATTO - Controllare ogni errore possibile e farne un print
3. FATTO - Controllare che la tabella spese non superi le 500 righe e abbia esattamente 4 colonne
4. FATTO - Quando la tabella sullo sheet è già popolata prima cancellare tutti i dati
5. FATTO - Stampare se ci sono record che hanno una categoria non gestita
6. Gestire i mesi non completati e quelli completati
7. FATTO - Nel job io farei prima cerca di autentificarsi a dropbox e google drive e verifica che funzionano poi tutto il resto.
8. FATTO - Pensare di non tenere sul repo i dati, questo ti evita anche i commit
9. Quando controllo o setto l'ordine delle colonne?
10. synch_entrate_totali ha tante cose hardcoded
11. Rifare il giro su 2025 e 2024
12. fare flag solo spese o solo entrate
13. fare action mauale con scelta raw -> prc -> scrittura oppure prc->scrittura
14. Stamapre il timestamp dell'ultimo aggiornamento
15. Non posso lanciare il flusso su anni precedenti per via delle add_rows che sono aggiornate sempre al presente

## Download dal dropbox
1. FATTO - Fare una funzione che automaticamente capisce anno e mese del file
2. FATTO - Gestire errore quando non trova il file nel dropdob


## Scrivere sul google sheet
1. FATTO - Fare la parte di scrittura delle Entrate



# Input e scelte:
* Cose fare se andando in automatico si trova un altro file raw con lo stesso anno e mese? potrei fare un controllo di ugualianza
* Flag per sovrascrivere dal processed al drive
* Flag per sovrascrivere da smistamento al raw
* Flag 
