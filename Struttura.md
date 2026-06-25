# Flusso del progetto

## processa_mese()

processa_mese()
    ├── prepara_percorsi()
    │       ├── se non c'è file app    -> termina/salta        [PROCESSA_TUTTI_I_MESI]
    │       ├── se non c'è csv         -> termina
    │       └── se esiste già output   -> termina/sovrascrive  [SOVRASCRIVI_OUTPUT]
    │
    │> stampa le directory dei file [STAMPA_PERCORSI]
    │
    │
    ├── prepara_spese()
    │       ├── seleziona_e_rinomina_colonne()
    │       └── aggiungi_righe_spese()
    ├── prepara_entrate()
    │       └── seleziona_e_rinomina_colonne()
    │
    │> stampa_duplicati spese()    [STAMPA_DUPLICATI]
    │> stampa_duplicati entrate()  [STAMPA_DUPLICATI]
    │> stampa_spese_altro()        [STAMPA_SPESE_ALTRO]│
    │
    ├── formatta_dataframe_output() spese()
    ├── formatta_dataframe_output() entrate()
    │
    └──esporta_excel()


## prepara_spese()
1. Legge dall'excel il foglio Spese
2. Pulisce il foglio   [seleziona_e_rinomina_colonne()]
3. Aggiunge le righe dal csv    [aggiungi_righe_spese()]
4. Formatta le date in datetime dd/mm/yyyy
5. Ordina per Data

## prepara_entrate()
1. Legge dall'excel il foglio Entrate
2. Pulisce il foglio   [seleziona_e_rinomina_colonne()]
3. Formatta le date in datetime dd/mm/yyyy
4. Inserisce la colonna Mese 
5. Ordina per Data





    




  