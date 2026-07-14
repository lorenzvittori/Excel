## NOME FILE: main_automatic.py
from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import google_drive_module  as gd_module
from ELABORATION    import processing_module    as pr_module
from datetime       import datetime
from typing import cast
import configuration as config
import pandas as pd
import os
import logger

FLAG_SCRITTURA_SUL_DRIVE = os.getenv("FLAG_SCRITTURA_SUL_DRIVE", default = "true").lower()    == "true"
FLAG_SOVRASCRIVI_SHEET   = os.getenv("FLAG_SOVRASCRIVI_SHEET", default = "true").lower()      == "true"
FLAG_SOVRASCRIVI_RAW_DBX = os.getenv("FLAG_SOVRASCRIVI_RAW_DBX", default = "true").lower()    == "true"
FLAG_LOG_DUPLICATI       = os.getenv("FLAG_LOG_DUPLICATI", default = "true").lower()          == "true"
FLAG_LOG_ALTRO           = os.getenv("FLAG_LOG_ALTRO", default = "true").lower()              == "true"

STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.Design()
PATH_CSV_ADD_ROWS       = STRUTTURA_REPOSITORY["FILE_ADD_ROWS"]

FILE_BROKEN = DESIGN.NOME_FILE_ROTTO

DROPBOX_CRED = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]

DROPBOX_RAW_FOLDER = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
DROPBOX_PRC_FOLDER = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
DROPBOX_TO_SORT_FOLDER = STRUTTURA_DROPBOX["FOLD_TO_SORT"]

FOGLIO_SPESE = DESIGN.NOME_FOGLIO_SPESE
FOGLIO_ENTRATE = DESIGN.NOME_FOGLIO_ENTRATE


## ============================================================ 1 - SMISTAMENTO DEL DROPBOX ============================================================
print("")
print("#" * 46)
print("FLUSSO AUTOMATICO")
print("#" * 46)
print()

logger.reset_fase()
logger.new_phase("SMISTAMENTO DEL DROPBOX")
logger.new_phase("Connessione al DropBox tramite API.")

dbx = db_module.get_dropbox_client(
    dropbox_credential = DROPBOX_CRED,
    dropbox_token = DROPBOX_TOKEN
)

logger.ok_mex("Connessione al DropBox: ✔ COMPLETATA")
logger.end_phase()

logger.new_phase("Smistamento dei file")

FILE_SMISTATI = db_module.smista_file_excel(
    dbx = dbx,
    dropbox_folder_destinazione = DROPBOX_RAW_FOLDER,
    dropbox_folder_origine = DROPBOX_TO_SORT_FOLDER,
    get_raw_name = config.get_raw_name,
    estesione_files = ".xlsx",
    target_broken_name = FILE_BROKEN,
    nome_colonna_data = DESIGN.spese.data.raw,
    righe_da_saltare = 1,
    flag_sovrascrivi_raw = FLAG_SOVRASCRIVI_RAW_DBX,
)

logger.end_phase()   # chiude "Smistamento dei file sul DropBox"
logger.end_phase()   # chiude "DROPBOX"


LIST_ANNO_MESE = FILE_SMISTATI["SMISTATI"]


if not LIST_ANNO_MESE:
    logger.error_mex("Nessun file conforme trovato da smistare")
    raise SystemExit



ERRORI = []

TOTALE_ANNO_MESE = len(LIST_ANNO_MESE)
this_anno_mese = 0
S = "S" if TOTALE_ANNO_MESE > 1 else ""

logger.separatore()
print(f"INIZIO FLUSSO AUTOMATICO DI {TOTALE_ANNO_MESE} FILE{S}:")

for i_anno_mese in LIST_ANNO_MESE:
    print(f"\t• {i_anno_mese["anno"]}-{i_anno_mese["mese_str"]}")
    
logger.separatore()

for i_anno_mese in LIST_ANNO_MESE:
    this_anno_mese += 1
    ANNO = i_anno_mese["anno"]
    MESE = i_anno_mese["mese_str"]
    
    logger.reset_fase()
    
    
    try:
        print("------------")
        print(f"Flusso {this_anno_mese}/{TOTALE_ANNO_MESE} - ANNO {ANNO} - MESE {MESE}")
        print("------------")
        print()
## ============================================================ 2 - DROPBOX, DOWNLOAD ============================================================
        logger.new_phase("DROPBOX - Download")

        NAME_RAW_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
        NAME_PROCESSED_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)

        RAW_DATAFRAME = db_module.get_dataframe_from_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_RAW_FOLDER,
            file_name = NAME_RAW_FILE
        )

        if isinstance(RAW_DATAFRAME, pd.DataFrame):
            logger.error_mex(f"Non esistono i fogli {FOGLIO_SPESE} e {FOGLIO_ENTRATE}")
            raise ValueError

        RAW_DATAFRAME = cast(dict[str, pd.DataFrame], RAW_DATAFRAME)

        if FOGLIO_SPESE not in RAW_DATAFRAME.keys():
            logger.error_mex(f"Non esiste il foglio {FOGLIO_SPESE}")
            raise ValueError

        if FOGLIO_ENTRATE not in RAW_DATAFRAME.keys():
            logger.error_mex(f"Non esiste il foglio {FOGLIO_ENTRATE}")
            raise ValueError

        logger.end_phase()   # chiude "DROPBOX"


## ============================================================ 3 - ELABORAZIONE SPESE ED ENTRATE ============================================================

        logger.new_phase("Pulizia e formattazione della tabella")

        PRC_DATAFRAME = pr_module.processa_dataframe(
            df_raw=RAW_DATAFRAME,
            anno=ANNO,
            mese_str=MESE,
            design = DESIGN,
            path_csv_add_rows= PATH_CSV_ADD_ROWS,
            flag_stampa_duplicati = FLAG_LOG_DUPLICATI,
            flag_stampa_spese_altro = FLAG_LOG_ALTRO)

        logger.ok_mex("Elaborazione: ✔ COMPLETATA")
        logger.end_phase()   # chiude "Pulizia e formattazione della tabella"

        
## ============================================================ 4 - SCRITTURA SU GOOGLE SHEET ============================================================
        logger.new_phase("GOOGLE DRIVE")

        GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]
        
        logger.new_phase("Connessione a Google Drive tramite API")
        client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
        logger.ok_mex("Connessione a Google Drive: ✔ COMPLETATA")
        logger.end_phase()
        

        #Controlla che il file spese abbia le giuste colonne:
        PRC_SPESE_DATAFRAME = PRC_DATAFRAME[FOGLIO_SPESE]
        
        
        
        colonne_spese_attuali = sorted(PRC_SPESE_DATAFRAME.columns)
        colonne_spese_attese = sorted(DESIGN.colonne_spese_PRC())

        if colonne_spese_attuali != colonne_spese_attese:
            logger.error_mex(
                corpo = "Colonne nel foglio spese non corrispondenti a quelle attese",
                dettaglio = [ f"colonne attuali : {colonne_spese_attuali}",
                            f"colonne attese : {colonne_spese_attese}"])
            raise ValueError()

        
        logger.new_phase("Scrittura SPESE su GoogleSheet")
        
        gd_module.sync_spese_mensili(
            client = client,
            df_spese_prc = PRC_SPESE_DATAFRAME,
            flag_sovrascrivi_celle = FLAG_SOVRASCRIVI_SHEET,
            id_google_sheet = config.ID_GOOGLE_SHEET[ANNO],
            nome_foglio_mese = FOGLIO_SPESE,
            num_col_sheet_spese = DESIGN.num_col_spese_PRC(),
            cell_spese_first_entry = DESIGN.CELLA_SPESE_FIRST_ENTRY,
            cell_spese_timestamp = DESIGN.CELLA_SPESE_TSTAMP
        )
        logger.ok_mex(f"Scrittura delle spese: ✔ COMPLETATA")
        logger.end_phase()   # chiude "Scrittura SPESE su GoogleSheet"
        
        
        logger.new_phase("Scrittura ENTRATE su GoogleSheet")
        PRC_ENTRATE_DATAFRAME = PRC_DATAFRAME[FOGLIO_ENTRATE]
        
        # ---- AGGIUNTA TIMESTAMP ENTRATE: stesso istante per tutte le righe di questa run ----
        timestamp_run = datetime.now().strftime("%d/%m/%Y %H.%M.%S")
        PRC_ENTRATE_DATAFRAME["TimeStamp"] = timestamp_run
        logger.info_mex(f"TimeStamp entrate: {timestamp_run}")

        colonne_entrate_attuali = sorted(PRC_ENTRATE_DATAFRAME.columns)
        colonne_entrate_attese = sorted(DESIGN.colonne_entrate_PRC())

        if colonne_entrate_attuali != colonne_entrate_attese:
            logger.error_mex(
                corpo = "Colonne nel foglio entrate non corrispondenti a quelle attese",
                dettaglio = [ f"colonne attuali : {colonne_entrate_attuali}",
                            f"colonne attese : {colonne_entrate_attese}"])
            raise ValueError()

    
        gd_module.sync_entrate_totali(
            client = client,
            anno = ANNO,
            mese_str = MESE,
            col_mese    =   DESIGN.entrate.mese.sheet,
            col_data    =   DESIGN.entrate.data.sheet,
            col_importo =   DESIGN.entrate.importo.sheet,
            col_note    =   DESIGN.entrate.note.sheet,
            col_timestamp = DESIGN.entrate.timestamp.sheet,
            top_left_entry = DESIGN.CELLA_ENTRATE_FIRST_ENTRY,
            id_google_sheet = config.ID_GOOGLE_SHEET[ANNO],
            nome_foglio = DESIGN.NOME_FOGLIO_TOTAL_ENTRATE,
            df_entrate_prc = PRC_ENTRATE_DATAFRAME)
        
        logger.ok_mex(f"Scrittura delle entrate: ✔ COMPLETATA")
        logger.end_phase()   # chiude "Scrittura ENTRATE su GoogleSheet"
        logger.end_phase()

## ============================================================ 5 - DROPBOX, UPLOAD ============================================================

        logger.new_phase("DROPBOX - Upload")
        db_module.upload_dataframe_to_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_PRC_FOLDER,
            file_name = NAME_PROCESSED_FILE,
            df = PRC_DATAFRAME,
            flag_sovrascrivi = True
        )
        logger.ok_mex(f"Upload di {DROPBOX_PRC_FOLDER}/{NAME_PROCESSED_FILE}: ✔ COMPLETATO")

        logger.end_phase()   # chiude "GOOGLE DRIVE"

        print("------------")
        print(f"✔ COMPLETATO: Flusso {this_anno_mese}/{TOTALE_ANNO_MESE}: ANNO {ANNO} - MESE {MESE}")
        print("------------")
        print()
        logger.separatore()

    except BaseException as e:
        print("------------")
        print(f"✗ FALLITO: Flusso {this_anno_mese}/{TOTALE_ANNO_MESE}: ANNO {ANNO} - MESE {MESE}")
        print(e)
        print("------------")
        print()
        ERRORI.append((ANNO, MESE, str(e)))
        continue

## ============================================================ 6 - LOG RIASSUNTIVO ============================================================
logger.separatore()
if ERRORI:
    logger.reset_fase()
    log_errori = []
    for anno_err, mese_err, errore in ERRORI:
        log_errori.append(f"ANNO {anno_err} MESE {mese_err}: {errore}")
    
    logger.warning_mex(
        corpo = f"{len(ERRORI)} su {len(LIST_ANNO_MESE)} file hanno fallito:",
        dettaglio = log_errori)
    
    logger.separatore()
    raise SystemExit
else:
    logger.info_mex(f"Tutti i {len(LIST_ANNO_MESE)} file sono stati processati con successo")
    logger.separatore()