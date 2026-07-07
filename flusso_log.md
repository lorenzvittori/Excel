## Legenda
- INFO: informazione, flusso continua normalmente
- WARNING: anomalia non bloccante, il file/step viene saltato ma il flusso continua
- ERROR: errore bloccante per il singolo elemento (es. file), ma il flusso generale continua con gli altri
- SystemExit / raise: interrompe l'intera esecuzione dello script

# FLUSSO_TOTALE
1. Prima capisce se deve fare il processo in automatico capendo anno e mese dal dropbox oppure ha ANNO e MESE in input
    * se non ci sono input:
        > ERRORE: Input non validi
        > SystemExit

2. Si connette al DROPBOX (**get_dropbox_client**)
    * Se non esiste il file delle credenziali:
        > ERROR: File credenziali dropbox non trovato: _Path_
        > FileNotFoundError
    * Se non esiste il file del token:
        > ERROR: File toekn dropbox non trovato: _Path_
        > FileNotFoundError
    * Se le credenziali non sono valide
        > ERROR: Credenziali non valide
        > ValueError


3. CASO ANNO_MESE AUTOMATICO
    1. Lancia smista_file_excel
        * Se non ci sono file da smistare
        >INFO
        * Se ci sono dei file BROKEN.xlsx li elimina e
        >INFO
        * Per ogni file da smistare:
            * INFO: nome del file
            * tenta di scaricare il file, altrimenti
            >ERRORE ma continua con il prossimo file
            * tenta di leggere il file scaricato, altrimenti * ERRORE ma continua con il prossimo file
            * controlla che la colonna_data esista, altrimenti
            >WARNING ma continua con il prossimo file
            * controlla che nella colonna_data ci siano date, altrimenti
            >WARNING ma continua con il prossimo file
            * Se esiste unico anno e mese:
                * assegna anno, mese, nuovo nome, nuovo path coerentemente
                * altrimenti broken
            * Prima di muovere il file nella cartella corrispondente controlla se esiste già. Se esiste:
                * Se è fleggata la sovrascrizione -> INFO
                * altrimenti -> WARNING e continua con il prossimo file
            * Muove e rinomina il file:
                * se ci riesce -> OK
                * altrimenti -> ERRORE, ApiError


# MODULO DROPBOX

## get_dropbox_client
1. Cerca le credenziali (APP_KEY, APP_SECRET, REFRESH_TOKEN) come variabili d'ambiente:
    * Se non esiste il file delle credenziali:
        > ERROR: File credenziali dropbox non trovato: _Path_
        > FileNotFoundError
    * Se non esiste il file del token:
        > ERROR: File toekn dropbox non trovato: _Path_
        > FileNotFoundError
2. Legge credenziali e token da file
3. Tenta la connessione a Dropbox e verifica l'account corrente
    * Se le credenziali non sono valide
        > ERROR: Credenziali non valide
        > ValueError

## get_dataframe_from_dropbox
1. Controlla che il file esista su Dropbox (files_get_metadata)
    * se non esiste:
        *
    >ERROR "File non trovato su Dropbox: {path}"
        *
    >INFO "File disponibili nella cartella remota:" + elenco dei file trovati nella cartella
        *
    >FileNotFoundError
2. Scarica il file in memoria
    >OK "File letto da Dropbox: {path}"
3. Legge il file con pandas (header=None, quindi senza promuovere nessuna riga a intestazione)
    * non stampa nulla in caso di successo
    * ritorna un dict[foglio, DataFrame] oppure un singolo DataFrame se sheet_name è specificato

## download_file_from_dropbox
1. Controlla che il file esista su Dropbox (files_get_metadata)
    * se non esiste:
    >ERROR "File non trovato su Dropbox: {path}"
    >INFO "File disponibili nella cartella remota:" + elenco dei file trovati nella cartella
    >FileNotFoundError
2. Controlla che la cartella di destinazione locale esista
    * se non esiste
    >ERROR + FileNotFoundError
3. Controlla se il file esiste già in locale
    * se esiste e blocca_se_esistente=True
    >ERROR "Download interrotto" e la funzione ritorna senza scaricare (nessuna eccezione)
    * se esiste e blocca_se_esistente=False
    >WARNING "sovrascritto" e procede
4. Scarica il file su disco
    >OK "Download completato: {path}"
    >INFO "File creato in: {path}"

## upload_dataframe_to_dropbox
1. Converte il/i DataFrame in un file Excel in memoria (un solo foglio se df è un DataFrame, più fogli se df è un dizionario)
    * non stampa nulla
2. Carica il file su Dropbox, sovrascrivendo o meno in base a flag_sovrascrivi
    >OK "Upload completato: {path}"
    * (non gestisce esplicitamente eventuali errori dell'API: se l'upload fallisce, l'eccezione di dropbox risale non gestita)

## smista_file_excel
1. Elenca tutti i file con l'estensione specificata nella cartella di origine
    * se nessun file trovato
    >INFO "Nessun file .xlsx trovato in {cartella}" e ritorna {"SMISTATI": [], "BROKEN": []}
2. Elimina tutti i file residui che iniziano con target_broken_name (broken di run precedenti)
    * per ogni file eliminato
    >INFO "Rimosso broken residuo: {nome}"
3. Per ogni file rimanente da processare:
    *
    >INFO "Controllo file: {nome}"
    * tenta il download
        * se fallisce
    >ERROR "Impossibile scaricare {nome}: {errore}" e passa al file successivo
    * tenta la lettura del primo foglio (skiprows=righe_da_saltare)
        * se fallisce
    >ERROR "Impossibile leggere {nome}: {errore} -> SALTATO (non spostato)" e passa al file successivo
    * controlla che nome_colonna_data sia tra le colonne
        * se assente
        >WARNING "Colonna non trovata -> SALTATO (non spostato)" e passa al file successivo
    * converte la colonna data e controlla che non siano tutte NaT
        * se tutte NaT
        >WARNING "Nessuna data valida trovata -> SALTATO (non spostato)" e passa al file successivo
    * verifica che tutte le date abbiano stesso anno e stesso mese
        * se conforme: calcola nuovo_nome tramite get_raw_name(anno, mese_str), destinazione = cartella destinazione
        * se non conforme:
            *
            >WARNING "{nome} contiene date di anni/mesi diversi -> rinominato in {nuovo_nome}"
            * nuovo_nome = target_broken_name (con progressivo se già presente uno nella stessa esecuzione), destinazione = cartella origine
    * controlla se il path di destinazione esiste già
        * se esiste e flag_sovrascrivi=False
        >WARNING "esiste già -> SALTATO" e passa al file successivo (il file NON viene aggiunto al risultato)
        * se esiste e flag_sovrascrivi=True
        >INFO "esistente eliminato per sovrascrittura"
    * sposta/rinomina il file
        * se riesce
        >OK "[CONFORME/NON CONFORME] {nome} -> {nuovo_path}" e il file viene aggiunto al dizionario di ritorno (chiave SMISTATI o BROKEN)
        * se fallisce
        >ERROR "Impossibile spostare {nome}: {errore}"
4. Ritorna un dizionario {"SMISTATI": [...], "BROKEN": [...]} con i dettagli di ogni file effettivamente spostato


# MODULO PROCESSING

## seleziona_e_rinomina_colonne
1. Controlla che tutte le colonne richieste (chiavi di mappa_colonne) siano presenti nel DataFrame
    * se mancano una o più colonne
    >ValueError("Colonne mancanti nel foglio {nome_foglio}: {colonne_mancanti}")
    * non stampa nulla in caso di successo
2. Ritorna il DataFrame filtrato sulle sole colonne richieste, rinominate secondo mappa_colonne

## formatta_dataframe_output
1. Formatta la colonna data in stringa "%d/%m/%Y" (stringa vuota se nulla)
2. Formatta la colonna importo in stringa con virgola come separatore decimale (stringa vuota se nulla)
    * non stampa nulla

## aggiungi_righe_spese
1. Legge il CSV delle righe aggiuntive
2. Costruisce la data da GiornoData + mese_str + anno e la converte in datetime (errori diventano NaT)
3. Seleziona le colonne data/categoria/importo e aggiunge una colonna note vuota
4. Concatena le nuove righe al DataFrame delle spese esistente
    * non stampa nulla

## prepara_spese
1. Promuove la riga con indice 1 a intestazione delle colonne (la riga 0 è titolo, la riga 1 è header vero)
    * non stampa nulla
2. Scarta le prime due righe (titolo + header ormai duplicato) e resetta l'indice
3. Seleziona e rinomina le colonne tramite seleziona_e_rinomina_colonne
    * eredita l'eventuale ValueError per colonne mancanti
4. Aggiunge le righe extra da CSV tramite aggiungi_righe_spese
5. Converte la colonna data in datetime e ordina il DataFrame per data
    * non stampa nulla

## prepara_entrate
1. Promuove la riga con indice 1 a intestazione delle colonne (stessa logica di prepara_spese)
2. Scarta le prime due righe e resetta l'indice
3. Seleziona e rinomina le colonne tramite seleziona_e_rinomina_colonne
    * eredita l'eventuale ValueError per colonne mancanti
4. Converte la colonna data in datetime, inserisce la colonna mese, ordina per data
    * non stampa nulla

## stampa_duplicati
1. Individua le righe duplicate nel DataFrame
    * se ce ne sono
    >WARNING "DUPLICATI TROVATI NELLE {nome_tabella}:" + elenco dei duplicati
    * altrimenti
    >INFO "{nome_tabella} senza duplicati"

## stampa_spese_altro
1. Filtra le righe con categoria "altro" (case insensitive, trim)
    * se ce ne sono
    >INFO "SPESSE CON CATEGORIA \"ALTRO\":" + elenco righe ordinate per data
    * altrimenti
    >INFO "Nessuna spesa con categoria \"Altro\"."

## processa_dataframe
1. Calcola i nomi dei file raw/processato e le directory coinvolte
    * non stampa nulla
2. Controlla che la directory del file raw esista
    * se non esiste
    >ERROR "{nome file} MANCANTE"
    >SystemExit
3. Controlla che il file delle righe aggiuntive esista
    * se non esiste
    >ERROR "{path} MANCANTE"
    >SystemExit
4. Se flag_stampa_percorsi=True (e non è un'elaborazione multi-mese):
    * stampa i percorsi di input e output
5. Estrae i DataFrame raw di Spese ed Entrate dal dizionario df_raw
    * non stampa nulla
6. Chiama prepara_spese e prepara_entrate
    * eredita eventuali ValueError da seleziona_e_rinomina_colonne
7. Se flag_stampa_duplicati=True (e non multi-mese):
    * chiama stampa_duplicati su entrambe le tabelle (INFO/WARNING come sopra)
8. Se flag_stampa_spese_altro=True (e non multi-mese):
    * chiama stampa_spese_altro (INFO come sopra)
9. Formatta entrambe le tabelle per l'output finale (formatta_dataframe_output)
    * non stampa nulla
10. Ritorna un dizionario {NOME_FOGLIO_SPESE: df, NOME_FOGLIO_ENTRATE: df}


# MODULO GOOGLE DRVE
## GET_GOOGLE_CLIENT

1. Recupera le credenziali del service account
    * Se la variabile d'ambiente GOOGLE_SERVICE_ACCOUNT esiste (GitHub Actions):
        * legge le credenziali da lì (JSON)
    * Altrimenti (fallback locale):
        * controlla che il file di credenziali esista, altrimenti
 >      FileNotFoundError
        * legge le credenziali dal file
2. Autorizza il client con gspread e lo ritorna
    * non stampa nulla in caso di successo

## SYNC_MONTH_LOCAL

## SYNC_MONTH_LOCAL

1. Apre lo spreadsheet Google Sheet corrispondente all'anno (id_google_sheet)
    * se non trovato
    >FileNotFoundError
    * se errore generico dell'API
    >RuntimeError

2. Apre il worksheet corrispondente al mese (NOME_SHEET_MESE)
    * se non trovato
    >FileNotFoundError

3. CHECK
    * Controlla se il foglio ha già valori scritti in B2:D2
        * se non è vuoto:
            * se flag_sovrascrivi_celle=False
            >ERROR + SystemExit
            * altrimenti
            >INFO "SOVRASCRIVO CELLE"
    * Controlla che le righe da scrivere non superino le 500
        * se le superano
        >WARN (non bloccante, procede comunque)
    * Controlla che il numero di colonne non superi NUMERO_COLONNE_SHEET_SPESE
        * se lo supera
        >ERROR + ValueError (bloccante)

4. WRITE
    * Svuota tutte le celle B2:D550 (per evitare residui di scritture precedenti più lunghe)
        * sempre
        >INFO
    * Scrive i dati del foglio Spese a partire da B1
        (i NaN vengono sostituiti con stringa vuota prima della scrittura)
        * non stampa nulla in caso di successo