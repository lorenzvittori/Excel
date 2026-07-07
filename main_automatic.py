## NOME FILE: FLUSSO_TOTALE.py
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

FOGLIO_SPESE = DESIGN["NOME_FOGLIO_SPESE"]
FOGLIO_ENTRATE = DESIGN["NOME_FOGLIO_ENTRATE"]


#DOWNLOAD FILE DAL DROPBOX
#fase 0
logger.reset_fase()

logger.fase("DROPBOX")
logger.inizio_istanza("Connessione al DropBox")

dbx = db_module.get_dropbox_client(
    dropbox_credential = DROPBOX_CRED,
    dropbox_token = DROPBOX_TOKEN
)

logger.fine_istanza()
    
logger.inizio_istanza("Smistamento dei file sul DropBox")

FILE_SMISTATI = db_module.smista_file_excel(
    dbx = dbx,
    dropbox_folder_destinazione = DROPBOX_RAW_FOLDER,
    dropbox_folder_origine = "",
    get_raw_name = config.get_raw_name,
    estesione_files = ".xlsx",
    target_broken_name = FILE_BROKEN,
    nome_colonna_data = NOMI_COLONNE_APP["COLONNE_SPESE"]["COL_SPESE_DATA"],
    righe_da_saltare = 1,
    flag_sovrascrivi_raw = FLAG_SOVRASCRIVI_RAW_DBX,
)
logger.fine_istanza()

LIST_ANNO_MESE = FILE_SMISTATI["SMISTATI"]


if not LIST_ANNO_MESE:
    logger.tipo_messaggio(
        tipo="ERRORE",
        corpo="Nessun file conforme trovato da smistare")
    raise SystemExit



ERRORI = []

TOTALE_ANNO_MESE = len(LIST_ANNO_MESE)
this_anno_mese = 0

logger.start(corpo = f"INIZIO FLUSSO AUTOMATICO DI {TOTALE_ANNO_MESE} FILES")

for i_anno_mese in LIST_ANNO_MESE:
    this_anno_mese += 1
    ANNO = i_anno_mese["anno"]
    MESE = i_anno_mese["mese_str"]
    
    logger.reset_fase()
    
    
    try:
        logger.separatore()
        print(f"Flusso {this_anno_mese}/{TOTALE_ANNO_MESE}", end = "")
        logger.inizio_flusso_anno_mese(anno = ANNO, mese_str = MESE)
        logger.fase("DROPBOX")

        NAME_RAW_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
        NAME_PROCESSED_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)

        RAW_DATAFRAME = db_module.get_dataframe_from_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_RAW_FOLDER,
            file_name = NAME_RAW_FILE
        )

        if isinstance(RAW_DATAFRAME, pd.DataFrame):
            logger.tipo_messaggio(
                tipo="ERRORE",
                corpo=f"Non esistono i fogli {FOGLIO_SPESE} e {FOGLIO_ENTRATE}"
            )
            raise ValueError

        RAW_DATAFRAME = cast(dict[str, pd.DataFrame], RAW_DATAFRAME)

        if FOGLIO_SPESE not in RAW_DATAFRAME.keys():
            logger.tipo_messaggio(
                tipo="ERRORE",
                corpo=f"Non esiste il foglio {FOGLIO_SPESE}"
            )
            raise ValueError

        if FOGLIO_ENTRATE not in RAW_DATAFRAME.keys():
            logger.tipo_messaggio(
                tipo="ERRORE",
                corpo=f"Non esiste il foglio {FOGLIO_ENTRATE}"
            )
            raise ValueError


        #PROCESSA MESE
        logger.fase("Pulizia e formattazione della tabella")

        logger.sottofase("Pulizia e formattazione")
        PRC_DATAFRAME = pr_module.processa_dataframe(
            df_raw=RAW_DATAFRAME,
            anno=ANNO,
            mese_str=MESE,
            design = DESIGN,
            path_csv_add_rows= PATH_CSV_ADD_ROWS,
            colonne_app = NOMI_COLONNE_APP,
            flag_stampa_duplicati = FLAG_LOG_DUPLICATI,
            flag_stampa_spese_altro = FLAG_LOG_ALTRO)

        
        #SCRITTURA SU GOOGLE DRIVE
        logger.fase("GOOGLE DRIVE")

        GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]
        
        logger.inizio_istanza("Connessione a Google Drive")
        client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
        logger.fine_istanza()
        

        #Controlla che il file spese abbia le giuste colonne:
        PRC_SPESE_DATAFRAME = PRC_DATAFRAME[FOGLIO_SPESE]

        colonne_spese_attuali = sorted(PRC_SPESE_DATAFRAME.columns)
        colonne_spese_attese = sorted([DESIGN[c] for c in NOMI_COLONNE_APP["COLONNE_SPESE"].keys()])

        if colonne_spese_attuali != colonne_spese_attese:
            logger.tipo_messaggio(
                    tipo = "ERRORE", 
                    corpo=  "Colonne nel foglio spese non corrispondenti a quelle attese",
                    dettaglio=[ f"colonne attuali : {colonne_spese_attuali}",
                                f"colonne attese : {colonne_spese_attese}"])
            raise ValueError()

        
        logger.inizio_istanza("Scrittura su sheet")
        gd_module.sync_month_local(
            client=client,
            anno=ANNO,
            mese_str=MESE,
            df_prc=PRC_DATAFRAME,
            flag_sovrascrivi_celle=FLAG_SOVRASCRIVI_SHEET
        )
        logger.fine_istanza()
        
        logger.inizio_istanza("Salvataggio della tabella processata")
        db_module.upload_dataframe_to_dropbox(
            dbx = dbx,
            dropbox_folder = DROPBOX_PRC_FOLDER,
            file_name = NAME_PROCESSED_FILE,
            df = PRC_DATAFRAME,
            flag_sovrascrivi = True
        )
        logger.fine_istanza()
        logger.fine(anno = ANNO, mese_str=MESE)
        logger.separatore()

    except Exception as e:
        logger.tipo_messaggio(
            tipo= "ERRORE",
            corpo = "Fallito il flusso per ANNO {ANNO} - MESE {MESE}:",
            dettaglio = f"{e}")
        ERRORI.append((ANNO, MESE, str(e)))
        continue


logger.separatore()
if ERRORI:
    log_errori = []
    for anno_err, mese_err, errore in ERRORI:
        log_errori.append(f"ANNO {anno_err} MESE {mese_err}: {errore}")
    
    logger.tipo_messaggio(
            tipo = "WARNING",
            corpo = f"{len(ERRORI)} su {len(LIST_ANNO_MESE)} file hanno fallito:",
            dettaglio=log_errori)
    
    logger.separatore()
    raise SystemExit
else:
    logger.tipo_messaggio(tipo = "INFO", corpo = f"Tutti i {len(LIST_ANNO_MESE)} file sono stati processati con successo")
    logger.separatore()
    