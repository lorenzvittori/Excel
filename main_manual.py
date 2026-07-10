from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import write_module         as gd_module
from ELABORATION    import processing_module    as pr_module
from datetime       import datetime
from typing import cast
import configuration as config  
import pandas as pd
import os
import logger

ANNO = os.getenv("ANNO", default = "2026")

MESE = os.getenv("MESE", default = "07")
MESE = config.MESI[MESE]["mese_str"]


FLAG_PRIORITIZZA_PRC     = os.getenv("FLAG_PRIORITIZZA_PRC",    default = "false").lower() == "true"
FLAG_SCRITTURA_SUL_DRIVE = os.getenv("FLAG_SCRITTURA_SUL_DRIVE",default = "false").lower() == "true"
FLAG_SOVRASCRIVI_SHEET   = os.getenv("FLAG_SOVRASCRIVI_SHEET",  default = "true").lower()  == "true"
FLAG_SOVRASCRIVI_RAW_DBX = os.getenv("FLAG_SOVRASCRIVI_RAW_DBX",default = "true").lower()  == "true"
FLAG_LOG_DUPLICATI       = os.getenv("FLAG_LOG_DUPLICATI",      default = "true").lower()  == "true"
FLAG_LOG_ALTRO           = os.getenv("FLAG_LOG_ALTRO",          default = "true").lower()  == "true"

STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.DESIGN
NOMI_COLONNE_APP        = config.NOMI_COLONNE_APP
PATH_CSV_ADD_ROWS       = STRUTTURA_REPOSITORY["FILE_ADD_ROWS"]

FILE_BROKEN = DESIGN["NOME_FILE_ROTTO"]

DROPBOX_CRED = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]

DROPBOX_RAW_FOLDER = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
DROPBOX_PRC_FOLDER = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
DROPBOX_TO_SORT_FOLDER = STRUTTURA_DROPBOX["FOLD_TO_SORT"]

FOGLIO_SPESE = DESIGN["NOME_FOGLIO_SPESE"]
FOGLIO_ENTRATE = DESIGN["NOME_FOGLIO_ENTRATE"]


flag_prioritizza_prc = True

## ============================================================ 1 - SMISTAMENTO DEL DROPBOX ============================================================
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
## ============================================================ 2 - DROPBOX, DOWNLOAD ============================================================
    logger.new_phase("DROPBOX - Download")

    logger.new_phase("Connessione al DropBox tramite API.")

    dbx = db_module.get_dropbox_client(
        dropbox_credential = DROPBOX_CRED,
        dropbox_token = DROPBOX_TOKEN
    )

    logger.ok_mex("Connessione al DropBox: ✔ COMPLETATA")
    logger.end_phase()

    NAME_RAW_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
    NAME_PROCESSED_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)
    
    # -- CONTROLLO ESISTENZA FILE
    logger.new_phase("Controllo presenza dei files")
    
    DROPBOX_RAW_DIR = f"{DROPBOX_RAW_FOLDER}/{NAME_RAW_FILE}"
    file_raw_disponibili = [f.name for f in dbx.files_list_folder(str(DROPBOX_RAW_FOLDER)).entries]  # type: ignore
    if NAME_RAW_FILE in file_raw_disponibili:
        logger.info_mex(f"Trovato file RAW: {DROPBOX_RAW_DIR}")
    else:
        logger.error_mex(
            corpo = f"File RAW inesistente",
            dettaglio = DROPBOX_RAW_DIR)
        raise ValueError
    
    DROPBOX_PRC_DIR = f"{DROPBOX_PRC_FOLDER}/{NAME_PROCESSED_FILE}"
    file_raw_disponibili = [f.name for f in dbx.files_list_folder(str(DROPBOX_PRC_FOLDER)).entries]  # type: ignore
    if NAME_PROCESSED_FILE in file_raw_disponibili:
        logger.info_mex(f"Trovato file PROCESSED: {DROPBOX_PRC_DIR}")
    else:
        logger.info_mex(f"File PRC inesistnte")
    
    logger.end_phase()
    
    
    if not flag_prioritizza_prc:
        logger.info_mex("USO IL FILE RAW")
        
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

        logger.end_all_phases()

    ## ============================================================ 3 - ELABORAZIONE SPESE ED ENTRATE ============================================================

        logger.new_phase("Pulizia e formattazione della tabella")

        PRC_DATAFRAME = pr_module.processa_dataframe(
            df_raw=RAW_DATAFRAME,
            anno=ANNO,
            mese_str=MESE,
            design = DESIGN,
            path_csv_add_rows= PATH_CSV_ADD_ROWS,
            colonne_app = NOMI_COLONNE_APP,
            flag_stampa_duplicati = FLAG_LOG_DUPLICATI,
            flag_stampa_spese_altro = FLAG_LOG_ALTRO)

        logger.ok_mex("Elaborazione: ✔ COMPLETATA")
        logger.end_phase()   # chiude "Pulizia e formattazione della tabella"
        
    else:
        logger.info_mex("USO IL FILE PRCOCESSED")
        
        PRC_DATAFRAME = db_module.get_dataframe_from_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_PRC_FOLDER,
            file_name = NAME_PROCESSED_FILE,
            header = 0
        )

        if isinstance(PRC_DATAFRAME, pd.DataFrame):
            logger.error_mex(f"Non esistono i fogli {FOGLIO_SPESE} e {FOGLIO_ENTRATE}")
            raise ValueError

        PRC_DATAFRAME = cast(dict[str, pd.DataFrame], PRC_DATAFRAME)

        if FOGLIO_SPESE not in PRC_DATAFRAME.keys():
            logger.error_mex(f"Non esiste il foglio {FOGLIO_SPESE}")
            raise ValueError

        if FOGLIO_ENTRATE not in PRC_DATAFRAME.keys():
            logger.error_mex(f"Non esiste il foglio {FOGLIO_ENTRATE}")
            raise ValueError
        
        
        logger.end_all_phases()

        
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
    colonne_spese_attese = sorted([DESIGN[k] for k in DESIGN.keys() if k.startswith("COL_SPESE")])

    if colonne_spese_attuali != colonne_spese_attese:
        logger.error_mex(
            corpo = "Colonne nel foglio spese non corrispondenti a quelle attese",
            dettaglio = [ f"colonne attuali : {colonne_spese_attuali}",
                        f"colonne attese : {colonne_spese_attese}"])
        raise ValueError()

    
    logger.new_phase("Scrittura SPESE su GoogleSheet")
    gd_module.sync_spese_mensili(
        client=client,
        anno=ANNO,
        mese_str=MESE,
        df_spese_prc=PRC_SPESE_DATAFRAME,
        flag_sovrascrivi_celle=FLAG_SOVRASCRIVI_SHEET
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
    colonne_entrate_attese = sorted([DESIGN[k] for k in DESIGN.keys() if k.startswith("COL_ENTRATE")])

    if colonne_entrate_attuali != colonne_entrate_attese:
        logger.error_mex(
            corpo = "Colonne nel foglio entrate non corrispondenti a quelle attese",
            dettaglio = [ f"colonne attuali : {colonne_entrate_attuali}",
                        f"colonne attese : {colonne_entrate_attese}"])
        raise ValueError()


    gd_module.sync_entrate_totali(
        client=client,
        anno=ANNO,
        mese_str=MESE,
        col_mese =      DESIGN["COL_ENTRATE_MESE"],
        col_data =      DESIGN["COL_ENTRATE_DATA"],
        col_importo =   DESIGN["COL_ENTRATE_IMPORTO"],
        col_note =      DESIGN["COL_ENTRATE_NOTE"],
        col_timestamp = DESIGN["COL_ENTRATE_TSTAMP"],
        top_left_entry =DESIGN["FIRST_ENTRY"],
        df_entrate_prc =PRC_ENTRATE_DATAFRAME)
    
    logger.ok_mex(f"Scrittura delle entrate: ✔ COMPLETATA")
    logger.end_phase()   # chiude "Scrittura ENTRATE su GoogleSheet"
    logger.end_phase()

## ============================================================ 5 - DROPBOX, UPLOAD ============================================================

    if not flag_prioritizza_prc:
        logger.new_phase("DROPBOX - Upload")
        db_module.upload_dataframe_to_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_PRC_FOLDER,
            file_name = NAME_PROCESSED_FILE,
            df = PRC_DATAFRAME,
            flag_sovrascrivi = True
        )
        logger.ok_mex(f"Upload di {DROPBOX_PRC_FOLDER}/{NAME_PROCESSED_FILE}: ✔ COMPLETATO")

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
