## NOME FILE: main_job_single.py
from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import google_drive_module  as gd_module
from ELABORATION    import processing_module    as pr_module
from datetime       import datetime
from typing import cast
import workflow as wf
import configuration as config 
import pandas as pd
import os
import logger

ANNO = os.getenv("ANNO", default = "2026")

MESE = os.getenv("MESE", default = "06")
MESE = config.MESI[MESE]["mese_str"]


FLAG_PRIORITIZZA_PRC     = os.getenv("FLAG_PRIORITIZZA_PRC",    default = "false").lower() == "true"
FLAG_SCRITTURA_SUL_DRIVE = os.getenv("FLAG_SCRITTURA_SUL_DRIVE",default = "false").lower() == "true"
FLAG_SOVRASCRIVI_SHEET   = os.getenv("FLAG_SOVRASCRIVI_SHEET",  default = "true").lower()  == "true"
FLAG_SOVRASCRIVI_RAW_DBX = os.getenv("FLAG_SOVRASCRIVI_RAW_DBX",default = "true").lower()  == "true"
FLAG_LOG_DUPLICATI       = os.getenv("FLAG_LOG_DUPLICATI",      default = "true").lower()  == "true"
FLAG_LOG_ALTRO           = os.getenv("FLAG_LOG_ALTRO",          default = "true").lower()  == "true"

STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.Design()


FILE_BROKEN = DESIGN.NOME_FILE_ROTTO

DROPBOX_CRED            = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN           = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]
PATH_CSV_ADD_ROWS       = STRUTTURA_REPOSITORY["FILE_ADD_ROWS"]
GOOGLE_SERVICE_ACCOUNT  = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]

DROPBOX_RAW_FOLDER      = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
DROPBOX_PRC_FOLDER      = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
DROPBOX_TO_SORT_FOLDER  = STRUTTURA_DROPBOX["FOLD_TO_SORT"]

FOGLIO_SPESE    = DESIGN.NOME_FOGLIO_SPESE
FOGLIO_ENTRATE  = DESIGN.NOME_FOGLIO_ENTRATE


## ========================================================================================================================
print("")
print("#" * logger.BLOCK_LENGTH)
print("FLUSSO MANUALE")
print("#" * logger.BLOCK_LENGTH)
print()

logger.reset_fase()

try:
    print("------------")
    print(f"Flusso ANNO {ANNO} - MESE {MESE}")
    print("------------")
    

    RAW_NAME_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
    PRC_NAME_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)
    
## ============================================================ 1 - DROPBOX, DOWNLOAD ============================================================
    logger.new_phase("DROPBOX - Download")

    #-----------
    logger.new_phase("Connessione al DropBox tramite API")
    dbx = db_module.get_dropbox_client(
        dropbox_credential = DROPBOX_CRED,
        dropbox_token = DROPBOX_TOKEN
    )
    logger.ok_mex("Connessione al DropBox: ✔ COMPLETATA")
    logger.end_phase()
    #-----------
    
    # -- CONTROLLO ESISTENZA FILE
    logger.new_phase("Controllo presenza dei files")
    
    DROPBOX_RAW_DIR = f"{DROPBOX_RAW_FOLDER}/{RAW_NAME_FILE}"
    file_raw_disponibili = [f.name for f in dbx.files_list_folder(str(DROPBOX_RAW_FOLDER)).entries]  # type: ignore
    if RAW_NAME_FILE in file_raw_disponibili:
        logger.info_mex(f"Trovato file RAW: {DROPBOX_RAW_DIR}")
    else:
        logger.error_mex(
            corpo = f"File RAW inesistente",
            dettaglio = DROPBOX_RAW_DIR)
        raise ValueError
    
    DROPBOX_PRC_DIR = f"{DROPBOX_PRC_FOLDER}/{PRC_NAME_FILE}"
    file_raw_disponibili = [f.name for f in dbx.files_list_folder(str(DROPBOX_PRC_FOLDER)).entries]  # type: ignore
    if PRC_NAME_FILE in file_raw_disponibili:
        logger.info_mex(f"Trovato file PROCESSED: {DROPBOX_PRC_DIR}")
    else:
        logger.info_mex(f"File PRC inesistnte")
    
    logger.end_phase()
    
    
    if not FLAG_PRIORITIZZA_PRC:
        logger.info_mex("USO IL FILE RAW")
        
        #-----------
        RAW_DATAFRAME = wf.download_dropbox(
            dbx                 = dbx,
            raw_name            = RAW_NAME_FILE,
            prc_name            = PRC_NAME_FILE,
            dropbox_raw_folder  = DROPBOX_RAW_FOLDER,
            dropbox_prc_folder  = DROPBOX_PRC_FOLDER,
            foglio_spese        = FOGLIO_SPESE,
            foglio_entrate      = FOGLIO_ENTRATE,
            prioritizza_prc     = False
            )
        #-----------

        logger.end_all_phases()

    ## ------------------------------------------------- 2 - ELABORAZIONE SPESE ED ENTRATE -------------------------------------------------
        PRC_DATAFRAME = wf.elabora_dataframe(
            df_raw                  = RAW_DATAFRAME,
            anno                    = int(ANNO),
            mese_str                = MESE,
            design                  = DESIGN,
            path_csv_add_rows       = PATH_CSV_ADD_ROWS,
            flag_stampa_duplicati   = FLAG_LOG_DUPLICATI,
            flag_stampa_spese_altro = FLAG_LOG_ALTRO
            )
        
    else:
        #-----------
        PRC_DATAFRAME = wf.download_dropbox(
            dbx                 = dbx,
            raw_name            = RAW_NAME_FILE,
            prc_name            = PRC_NAME_FILE,
            dropbox_raw_folder  = DROPBOX_RAW_FOLDER,
            dropbox_prc_folder  = DROPBOX_PRC_FOLDER,
            foglio_spese        = FOGLIO_SPESE,
            foglio_entrate      = FOGLIO_ENTRATE,
            prioritizza_prc     = True
            )
        #-----------
        logger.end_all_phases()

        
## ============================================================ 3 - SCRITTURA SU GOOGLE SHEET ============================================================
    logger.new_phase("GOOGLE DRIVE")

    #-----------
    logger.new_phase("Connessione a Google Drive tramite API")
    client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
    logger.ok_mex("Connessione a Google Drive: ✔ COMPLETATA")
    logger.end_phase()
    #-----------

    #Controlla che il file spese abbia le giuste colonne:
    PRC_SPESE_DATAFRAME     = PRC_DATAFRAME[FOGLIO_SPESE]
    PRC_ENTRATE_DATAFRAME   = PRC_DATAFRAME[FOGLIO_ENTRATE]
    
    #-----------
    wf.scrivi_google_sheet(
        client                  = client,
        df_spese_prc            = PRC_SPESE_DATAFRAME,
        design                  = DESIGN,
        anno                    = int(ANNO),
        id_google_sheet         = config.ID_GOOGLE_SHEET[ANNO],
        nome_foglio_mese        = config.MESI[MESE]["nome_foglio_associato"],
        nome_foglio_entrate     = DESIGN.NOME_FOGLIO_TOTAL_ENTRATE,
        mese_str                = MESE,
        flag_sovrascrivi_celle  = FLAG_SOVRASCRIVI_SHEET,
        df_entrate_prc          = PRC_ENTRATE_DATAFRAME,
        )
    #-----------
    
    logger.end_phase()
## ============================================================ 5 - DROPBOX, UPLOAD ============================================================

    if not FLAG_PRIORITIZZA_PRC:
        #-----------
        wf.upload_dropbox(
            dbx                 = dbx,
            dropbox_prc_folder  = DROPBOX_PRC_FOLDER,
            prc_file_name       = PRC_NAME_FILE,
            df_prc              = PRC_DATAFRAME,
            )
        #-----------

    logger.end_all_phases()

    print("------------")
    print(f"✔ COMPLETATO: Flusso ANNO {ANNO} - MESE {MESE}")
    print("------------")
    print()
    logger.separatore()

except BaseException:
    print("------------")
    print(f"✗ FALLITO: Flusso ANNO {ANNO} - MESE {MESE}")
    print("------------")
    print()
