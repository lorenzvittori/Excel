from DROPBOX import dropbox_module as db_module
import configuration as config
import pandas as pd
from pathlib import Path


DROPBOX_CRED = config.STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN = config.STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]
DROPBOX_FOLDER = config.STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
FILE_NAME = "p_2026_06.xlsx"
FILE_PATH = Path("Dati/TabelleProcessed") / FILE_NAME
dbx = db_module.get_dropbox_client(DROPBOX_CRED, DROPBOX_TOKEN)

DF = pd.read_excel(
    FILE_PATH,
    sheet_name="Spese",
    skiprows=1,
    header=0
)

db_module.upload_dataframe_to_dropbox(
    dbx=dbx,
    dropbox_folder=DROPBOX_FOLDER,
    file_name=FILE_NAME,
    df=DF,
    flag_sovrascrivi=True
)
    