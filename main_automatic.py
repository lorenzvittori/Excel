## NOME FILE: main_automatic.py
from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import write_module         as gd_module
from ELABORATION    import processing_module    as pr_module
from typing import cast
import configuration as config  
import pandas as pd
import os
import logger

FLAG_SCRITTURA_SUL_DRIVE = os.getenv("FLAG_SCRITTURA_SUL_DRIVE", default = "false").lower()    == "true"
FLAG_SOVRASCRIVI_SHEET   = os.getenv("FLAG_SOVRASCRIVI_SHEET", default = "false").lower()      == "true"
FLAG_SOVRASCRIVI_RAW_DBX = os.getenv("FLAG_SOVRASCRIVI_RAW_DBX", default = "false").lower()    == "true"
FLAG_LOG_DUPLICATI       = os.getenv("FLAG_LOG_DUPLICATI", default = "false").lower()          == "true"
FLAG_LOG_ALTRO           = os.getenv("FLAG_LOG_ALTRO", default = "false").lower()              == "true"

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


#DOWNLOAD FILE DAL DROPBOX
#fase 0
print("\n\n\n")
logger.reset_fase()

logger.new_phase("DROPBOX")
logger.info_mex("Connessione al DropBox")

dbx = db_module.get_dropbox_client(
    dropbox_credential = DROPBOX_CRED,
    dropbox_token = DROPBOX_TOKEN
)

logger.info_mex("Connesso al DropBox")

logger.new_phase("Smistamento dei file sul DropBox")

FILE_SMISTATI = db_module.smista_file_excel(
    dbx = dbx,
    dropbox_folder_destinazione = DROPBOX_RAW_FOLDER,
    dropbox_folder_origine = DROPBOX_TO_SORT_FOLDER,
    get_raw_name = config.get_raw_name,
    estesione_files = ".xlsx",
    target_broken_name = FILE_BROKEN,
    nome_colonna_data = NOMI_COLONNE_APP["COLONNE_SPESE"]["COL_SPESE_DATA"],
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

logger.separatore()
print(f"INIZIO FLUSSO AUTOMATICO DI {TOTALE_ANNO_MESE} FILES")
logger.separatore()

for i_anno_mese in LIST_ANNO_MESE:
    this_anno_mese += 1
    ANNO = i_anno_mese["anno"]
    MESE = i_anno_mese["mese_str"]
    
    logger.reset_fase()
    
    
    try:
        logger.separatore()
        print(f"Flusso {this_anno_mese}/{TOTALE_ANNO_MESE} - ANNO {ANNO} - MESE {MESE}")

        logger.new_phase("DROPBOX")

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


        #PROCESSA MESE
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

        logger.end_phase()   # chiude "Pulizia e formattazione della tabella"

        
        #SCRITTURA SU GOOGLE DRIVE
        logger.new_phase("GOOGLE DRIVE")

        GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]
        
        logger.info_mex("Connessione a Google Drive")
        client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
        logger.info_mex("Connesso a Google Drive")
        

        #Controlla che il file spese abbia le giuste colonne:
        PRC_SPESE_DATAFRAME = PRC_DATAFRAME[FOGLIO_SPESE]

        colonne_spese_attuali = sorted(PRC_SPESE_DATAFRAME.columns)
        colonne_spese_attese = sorted([DESIGN[c] for c in NOMI_COLONNE_APP["COLONNE_SPESE"].keys()])

        if colonne_spese_attuali != colonne_spese_attese:
            logger.error_mex(
                corpo = "Colonne nel foglio spese non corrispondenti a quelle attese",
                dettaglio = [ f"colonne attuali : {colonne_spese_attuali}",
                              f"colonne attese : {colonne_spese_attese}"])
            raise ValueError()

        
        logger.new_phase("Scrittura su sheet")
        gd_module.sync_month_local(
            client=client,
            anno=ANNO,
            mese_str=MESE,
            df_prc=PRC_DATAFRAME,
            flag_sovrascrivi_celle=FLAG_SOVRASCRIVI_SHEET
        )
        logger.end_phase()   # chiude "Scrittura su sheet"
        
        
        logger.info_mex("Salvataggio della tabella processata su Dropbox")
        db_module.upload_dataframe_to_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_PRC_FOLDER,
            file_name = NAME_PROCESSED_FILE,
            df = PRC_DATAFRAME,
            flag_sovrascrivi = True
        )
        logger.info_mex("Tabella processata salvata su Dropbox")

        logger.end_phase()   # chiude "GOOGLE DRIVE"

        logger.info_mex(f"Flusso completato per ANNO {ANNO} - MESE {MESE}")
        logger.separatore()

    except BaseException as e:
        logger.error_mex(
            corpo = f"Fallito il flusso per ANNO {ANNO} - MESE {MESE}",
            dettaglio = str(e))
        ERRORI.append((ANNO, MESE, str(e)))
        continue


logger.separatore()
if ERRORI:
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