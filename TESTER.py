## NOME FILE: TESTER.py
"""
Script di verifica visiva per logger.py.
Nessuna dipendenza esterna (Dropbox, Google) - testa solo l'output del logger.
"""
import configuration as config
import logger
import pandas as pd
from pathlib import Path
from GOOGLE_DRIVE import write_module as gd_module


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



#SCRITTURA SU GOOGLE DRIVE
logger.new_phase("GOOGLE DRIVE")

GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]

logger.info_mex("Connessione a Google Drive")
client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
logger.info_mex("Connesso a Google Drive")

file_path = Path("DataBase/sheet_PROCESSED/p_2026_06.xlsx")

#Controlla che il file spese abbia le giuste colonne:
PRC_DATAFRAME = pd.read_excel(file_path, sheet_name="Entrate")

print("Stampa entrate locali:")
print(PRC_DATAFRAME)
print()

gd_module.sync_entrate_totali(
    df_entrate_prc=PRC_DATAFRAME,
    anno = "2026",
    mese_str= "06",
    client=client
)