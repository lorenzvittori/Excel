from DROPBOX import dropbox_module as db_module
import configuration as config
import pandas as pd
from pathlib import Path


DROPBOX_CRED = config.STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN = config.STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]
DROPBOX_FOLDER = config.STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
FILE_NAME = "app_2026_06.xlsx"
FILE_PATH = Path("Dati/TabelleApp") / FILE_NAME
dbx = db_module.get_dropbox_client(DROPBOX_CRED, DROPBOX_TOKEN)

DF = pd.read_excel(FILE_PATH, header=None)


DF.columns = DF.iloc[1] 
DF.columns.name = None     
print(DF.head(3))              
DF = DF.iloc[2:].reset_index(drop=True)         
print(DF.head(3))