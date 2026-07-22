## NOME FILE: main_job_auto.py
from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import google_drive_module  as gd_module
from ELABORATION    import processing_module    as pr_module
import scripts.workflow as wf
import configuration.configuration as config
import os
import configuration.logger as logger

FLAG_SCRITTURA_SUL_DRIVE = os.getenv("FLAG_SCRITTURA_SUL_DRIVE", default = "true").lower()    == "true"
FLAG_SOVRASCRIVI_SHEET   = os.getenv("FLAG_SOVRASCRIVI_SHEET", default = "true").lower()      == "true"
FLAG_SOVRASCRIVI_RAW_DBX = os.getenv("FLAG_SOVRASCRIVI_RAW_DBX", default = "true").lower()    == "true"
FLAG_LOG_DUPLICATI       = os.getenv("FLAG_LOG_DUPLICATI", default = "true").lower()          == "true"
FLAG_LOG_ALTRO           = os.getenv("FLAG_LOG_ALTRO", default = "true").lower()              == "true"

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

## ============================================================ 1 - SMISTAMENTO DEL DROPBOX ============================================================
print("")
print("#" * 46)
print("FLUSSO AUTOMATICO")
print("#" * 46)
print()

logger.reset_fase()
logger.new_phase("SMISTAMENTO DEL DROPBOX")

#-----------
logger.new_phase("Connessione al DropBox tramite API.")
dbx = db_module.get_dropbox_client(
    dropbox_credential = DROPBOX_CRED,
    dropbox_token = DROPBOX_TOKEN
)
logger.ok_mex("Connessione al DropBox: ✔ COMPLETATA")
logger.end_phase()
#-----------

#-----------
logger.new_phase("Connessione a Google Drive tramite API")
client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
logger.ok_mex("Connessione a Google Drive: ✔ COMPLETATA")
logger.end_phase()
#-----------

#-----------
LIST_ANNO_MESE = wf.smista_dropbox(
    dbx = dbx,
    dropbox_folder_origine = DROPBOX_TO_SORT_FOLDER,
    dropbox_folder_destinazione = DROPBOX_RAW_FOLDER,
    target_broken_name = FILE_BROKEN,
    nome_colonna_data = DESIGN.spese.data.raw,
    righe_da_saltare = 1,
    flag_sovrascrivi_raw = FLAG_SOVRASCRIVI_RAW_DBX,
    get_raw_name = config.get_raw_name
    )
#-----------
logger.end_phase()
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

    RAW_NAME_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
    PRC_NAME_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)
    
    
    try:
        print("------------")
        print(f"Flusso {this_anno_mese}/{TOTALE_ANNO_MESE} - ANNO {ANNO} - MESE {MESE}")
        print("------------")
        print()
## ============================================================ 2 - DROPBOX, DOWNLOAD ============================================================
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
## ============================================================ 3 - ELABORAZIONE SPESE ED ENTRATE ============================================================
        PRC_DATAFRAME = wf.elabora_dataframe(
            df_raw                  = RAW_DATAFRAME,
            anno                    = int(ANNO),
            mese_str                = MESE,
            design                  = DESIGN,
            path_csv_add_rows       = PATH_CSV_ADD_ROWS,
            flag_stampa_duplicati   = FLAG_LOG_DUPLICATI,
            flag_stampa_spese_altro = FLAG_LOG_ALTRO
            )
## ============================================================ 4 - SCRITTURA SU GOOGLE SHEET ============================================================
        logger.new_phase("GOOGLE DRIVE")

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
        #-----------
        wf.upload_dropbox(
            dbx                 = dbx,
            dropbox_prc_folder  = DROPBOX_PRC_FOLDER,
            prc_file_name       = PRC_NAME_FILE,
            df_prc              = PRC_DATAFRAME,
            )
        #-----------

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