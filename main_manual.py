## NOME FILE: main_manual.py

from DROPBOX import dropbox_module as db_module
from GOOGLE_DRIVE import google_drive_module as gd_module

import scripts.workflow as wf
import configuration.configuration as config
import configuration.logger as logger

ANNO_MESE_INPUT_DICT = {
    "2026_01": 0,
    "2026_02": 0,
    "2026_03": 0,
    "2026_04": 0,
    "2026_05": 0,
    "2026_06": 0,
    "2026_07": 0,
    "2026_08": 0,
    "2026_09": 0,
    "2026_10": 0,
    "2026_11": 0,
    "2026_12": 0,
}

FLAG_PRIORITIZZA_PRC     = False
FLAG_SCRITTURA_SUL_DRIVE = True
FLAG_SOVRASCRIVI_SHEET   = True
FLAG_SOVRASCRIVI_RAW_DBX = True
FLAG_LOG_DUPLICATI       = True
FLAG_LOG_ALTRO           = True

STRUTTURA_REPOSITORY = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX = config.STRUTTURA_DROPBOX
DESIGN = config.Design()

FILE_BROKEN = DESIGN.NOME_FILE_ROTTO

DROPBOX_CRED = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]
PATH_CSV_ADD_ROWS = STRUTTURA_REPOSITORY["FILE_ADD_ROWS"]
GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]

DROPBOX_RAW_FOLDER = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
DROPBOX_PRC_FOLDER = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
DROPBOX_TO_SORT_FOLDER = STRUTTURA_DROPBOX["FOLD_TO_SORT"]

FOGLIO_SPESE = DESIGN.NOME_FOGLIO_SPESE
FOGLIO_ENTRATE = DESIGN.NOME_FOGLIO_ENTRATE

logger.set_indentazione("\t")

print()
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
    if mask
]

if not LIST_ANNO_MESE:
    logger.error_mex("Nessun mese selezionato")
    raise SystemExit

logger.new_phase("Connessione al DropBox tramite API")

dbx = db_module.get_dropbox_client(
    dropbox_credential=DROPBOX_CRED,
    dropbox_token=DROPBOX_TOKEN,
)

logger.ok_mex("Connessione al DropBox: ✔ COMPLETATA")
logger.end_phase()

logger.new_phase("Connessione a Google Drive tramite API")

client = gd_module.get_google_client(
    google_service_account=GOOGLE_SERVICE_ACCOUNT
)

logger.ok_mex("Connessione a Google Drive: ✔ COMPLETATA")
logger.end_phase()

FALLITI = []
SUCCESSI = []

TOTALE_ANNO_MESE = len(LIST_ANNO_MESE)
S = "S" if TOTALE_ANNO_MESE > 1 else ""

logger.separatore()
print(f"INIZIO FLUSSO MANUALE DI {TOTALE_ANNO_MESE} FILE{S}:")

for item in LIST_ANNO_MESE:
    print(f"\t• {item['anno']}-{item['mese_str']}")

logger.separatore()

for idx, item in enumerate(LIST_ANNO_MESE, start=1):

    ANNO = item["anno"]
    MESE = item["mese_str"]

    RAW_NAME_FILE = config.get_raw_name(
        anno=ANNO,
        mese_str=MESE,
    )

    PRC_NAME_FILE = config.get_prc_name(
        anno=ANNO,
        mese_str=MESE,
    )

    logger.reset_fase()

    try:

        print("------------")
        print(f"Flusso {idx}/{TOTALE_ANNO_MESE} - ANNO {ANNO} - MESE {MESE}")
        print("------------")
        print()
        
        # ============================================================ 2 - DROPBOX, DOWNLOAD ============================================================
        DATAFRAME = wf.download_dropbox(
            dbx=dbx,
            raw_name=RAW_NAME_FILE,
            prc_name=PRC_NAME_FILE,
            dropbox_raw_folder=DROPBOX_RAW_FOLDER,
            dropbox_prc_folder=DROPBOX_PRC_FOLDER,
            foglio_spese=FOGLIO_SPESE,
            foglio_entrate=FOGLIO_ENTRATE,
            prioritizza_prc=FLAG_PRIORITIZZA_PRC,
        )
        # ============================================================ 3 - ELABORAZIONE ============================================================
        if not FLAG_PRIORITIZZA_PRC:
            PRC_DATAFRAME = wf.elabora_dataframe(
                df_raw=DATAFRAME,
                anno=int(ANNO),
                mese_str=MESE,
                design=DESIGN,
                path_csv_add_rows=PATH_CSV_ADD_ROWS,
                flag_stampa_duplicati=FLAG_LOG_DUPLICATI,
                flag_stampa_spese_altro=FLAG_LOG_ALTRO,
            )
        else:
            PRC_DATAFRAME = DATAFRAME
        # ============================================================ 4 - GOOGLE SHEET ============================================================
        if FLAG_SCRITTURA_SUL_DRIVE:

            PRC_SPESE_DATAFRAME = PRC_DATAFRAME[FOGLIO_SPESE]
            PRC_ENTRATE_DATAFRAME = PRC_DATAFRAME[FOGLIO_ENTRATE]

            wf.scrivi_google_sheet(
                client=client,
                df_spese_prc=PRC_SPESE_DATAFRAME,
                design=DESIGN,
                anno=int(ANNO),
                id_google_sheet=config.ID_GOOGLE_SHEET[ANNO],
                nome_foglio_mese=config.MESI[MESE]["nome_foglio_associato"],
                nome_foglio_entrate=DESIGN.NOME_FOGLIO_TOTAL_ENTRATE,
                mese_str=MESE,
                flag_sovrascrivi_celle=FLAG_SOVRASCRIVI_SHEET,
                df_entrate_prc=PRC_ENTRATE_DATAFRAME,
            )

        # ============================================================ 5 - DROPBOX, UPLOAD ============================================================
        if not FLAG_PRIORITIZZA_PRC:
            #-------------------
            wf.upload_dropbox(
                dbx=dbx,
                dropbox_prc_folder=DROPBOX_PRC_FOLDER,
                prc_file_name=PRC_NAME_FILE,
                df_prc=PRC_DATAFRAME,
            )
            #-------------------
        
        print("------------")
        print(
            f"✔ COMPLETATO: Flusso {idx}/{TOTALE_ANNO_MESE}: "
            f"ANNO {ANNO} - MESE {MESE}")
        print("------------")
        logger.separatore()
        print()
        SUCCESSI.append((ANNO, MESE))
        
    except BaseException as e:
        print("------------")
        print(
            f"✗ FALLITO: Flusso {idx}/{TOTALE_ANNO_MESE}: "
            f"ANNO {ANNO} - MESE {MESE}")
        print(e)
        print("------------")
        print()

        FALLITI.append((ANNO, MESE, str(e)))
        logger.separatore()
        continue

# ============================================================ 6 - LOG RIASSUNTIVO ============================================================
logger.separatore()
if FALLITI:
    logger.reset_fase()
    dettagli = [
        f"ANNO {anno} MESE {mese}: {errore}"
        for anno, mese, errore in FALLITI]
    logger.warning_mex(
        corpo=f"{len(FALLITI)} su {TOTALE_ANNO_MESE} file hanno fallito:",
        dettaglio=dettagli)

    if SUCCESSI:
        logger.info_mex(
            corpo=f"{len(SUCCESSI)} file completati correttamente:",
            dettaglio=[
                f"ANNO {anno} MESE {mese}"
                for anno, mese in SUCCESSI
            ],
        )
    logger.separatore()
    raise SystemExit(1)
else:
    logger.info_mex(f"Tutti i {len(SUCCESSI)} file sono stati processati con successo")
    logger.separatore()