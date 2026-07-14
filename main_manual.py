from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import google_drive_module         as gd_module
from ELABORATION    import processing_module    as pr_module
from datetime       import datetime
from typing import cast
import configuration as config
import pandas as pd
import logger

ANNO_MESE_INPUT_DICT = {
    "2026_01": 0,   
    "2026_02": 0,   
    "2026_03": 0,   
    "2026_04": 0,   
    "2026_05": 0,   
    "2026_06": 0,   
    "2026_07": 1,
    "2026_08": 0,   
    "2026_09": 0,   
    "2026_10": 0,   
    "2026_11": 0,   
    "2026_12": 0
}

FLAG_PRIORITIZZA_PRC     = 0
FLAG_SCRITTURA_SUL_DRIVE = 1
FLAG_SOVRASCRIVI_SHEET   = 1
FLAG_SOVRASCRIVI_RAW_DBX = 1
FLAG_LOG_DUPLICATI       = 1
FLAG_LOG_ALTRO           = 1

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

logger.set_indentazione("\t")


## ============================================================ 1 - SMISTAMENTO DEL DROPBOX ============================================================
print("")
print("#" * logger.BLOCK_LENGTH)
print("FLUSSO MANUALE")
print("#" * logger.BLOCK_LENGTH)
print()

logger.reset_fase()

LIST_ANNO_MESE = [
    {
        "anno": x[:4],
        "mese_str": x[5:]
    }
    for x, mask in ANNO_MESE_INPUT_DICT.items()
    if mask == 1
]

if not LIST_ANNO_MESE:
    logger.error_mex("Nessun file conforme trovato da smistare")
    raise SystemExit


FALLITI = []
SUCCESSI = []

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

        logger.new_phase("Connessione al DropBox tramite API")

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
        
        
        if not FLAG_PRIORITIZZA_PRC:
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
                flag_stampa_duplicati = bool(FLAG_LOG_DUPLICATI),
                flag_stampa_spese_altro = bool(FLAG_LOG_ALTRO)
            )

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
            flag_sovrascrivi_celle = bool(FLAG_SOVRASCRIVI_SHEET),
            id_google_sheet = config.ID_GOOGLE_SHEET[ANNO],
            nome_foglio_mese = config.MESI[MESE]["nome_foglio_associato"],
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

        if not FLAG_PRIORITIZZA_PRC:
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
        print(f"✔ COMPLETATO: Flusso {this_anno_mese}/{TOTALE_ANNO_MESE}: ANNO {ANNO} - MESE {MESE}")
        print("------------")
        logger.separatore()
        print()
        
        SUCCESSI.append((ANNO, MESE))

    except BaseException as e:
        print("------------")
        print(f"✗ FALLITO: Flusso {this_anno_mese}/{TOTALE_ANNO_MESE}: ANNO {ANNO} - MESE {MESE}")
        if not str(e).strip() == "":
            print(e)
        print("------------")
        logger.separatore()
        print()
        FALLITI.append((ANNO, MESE, str(e)))
        continue

## ============================================================ 6 - LOG RIASSUNTIVO ============================================================
logger.separatore()
if FALLITI or SUCCESSI:
    if SUCCESSI:
        logger.reset_fase()
            
        print(f"SUCCESSI:\t{len(LIST_ANNO_MESE) - len(FALLITI)} su {len(LIST_ANNO_MESE)}:")
        
        for anno_err, mese_err in SUCCESSI:
            print(f"\t• {anno_err}-{mese_err}")
    
    
    if FALLITI:
        logger.reset_fase()
        
        print(f"FALLITI:\t{len(FALLITI)} su {len(LIST_ANNO_MESE)}:")
        
        for anno_err, mese_err, errore in FALLITI:
            print(f"\t• {anno_err}-{mese_err}: {errore}")
        
    logger.separatore()