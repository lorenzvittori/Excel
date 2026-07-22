from DROPBOX        import dropbox_module       as db_module
from GOOGLE_DRIVE   import google_drive_module  as gd_module
from ELABORATION    import processing_module    as pr_module
import configuration.configuration as config
import configuration.logger as logger

from datetime       import datetime
from typing     import cast
from pathlib    import Path
import pandas as pd
import os
import io


"""

STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.Design
NOMI_COLONNE_APP        = config.NOMI_COLONNE_APP
PATH_CSV_ADD_ROWS       = STRUTTURA_REPOSITORY["FILE_ADD_ROWS"]

FILE_BROKEN = DESIGN.NOME_FILE_ROTTO

DROPBOX_CRED = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
DROPBOX_TOKEN = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]

DROPBOX_RAW_FOLDER = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
DROPBOX_PRC_FOLDER = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
DROPBOX_TO_SORT_FOLDER = STRUTTURA_DROPBOX["FOLD_TO_SORT"]

FOGLIO_SPESE = DESIGN.NOME_FOGLIO_SPESE
FOGLIO_ENTRATE = DESIGN.NOME_FOGLIO_ENTRATE

GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]

ID_GOOGLE_SHEET = config.ID_GOOGLE_SHEET



anno = 2025
sheet_spese = "TOTAL_spese"
rage_spese = "A1:G1000"
sheet_entrate = "TOTAL_entrate"
rage_entrate = "A1:G1000"



dbx = db_module.get_dropbox_client(
    dropbox_credential = DROPBOX_CRED,
    dropbox_token = DROPBOX_TOKEN
)

client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)


df_spese = gd_module.get_dataframe_from_google_sheet(
    client = client,
    id_google_sheet = ID_GOOGLE_SHEET[str(anno)],
    sheet_name=sheet_spese,
    table_range=rage_spese,
    header=True
)

df_entrate = gd_module.get_dataframe_from_google_sheet(
    client = client,
    id_google_sheet = ID_GOOGLE_SHEET[str(anno)],
    sheet_name="TOTAL_entrate",
    table_range=rage_entrate,
    header=True
) 


data_oggi = datetime.date.today().strftime("%d_%m_%y")

with pd.ExcelWriter(Path(f"DataBase/sheet_BACKUP/bk{anno}_{data_oggi}.xlsx"), engine="openpyxl") as writer:
    df_spese.to_excel(writer, sheet_name="Spese", index=False)
    df_entrate.to_excel(writer, sheet_name="Entrate", index=False)
    
    
"""