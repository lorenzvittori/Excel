## NOME FILE: FLUSSO_TOTALE.py
from DROPBOX import dropbox_module as db_module
from GOOGLE_DRIVE import write_module as gd_module
from pathlib import Path
from typing import cast
import main_module as m_module
import configuration as config  
import pandas as pd
import os


FLAG_AUTO_ANNO_MESE = os.getenv("FLAG_AUTO_ANNO_MESE", "true").lower() == "true"
ANNO = os.getenv("ANNO", "2026")
MESE = os.getenv("MESE", "07")

if not FLAG_AUTO_ANNO_MESE and (not ANNO or not MESE):
    print("[ERROR]\t Modalità manuale (automatico=false) richiede ANNO e MESE specificati")
    raise SystemExit


STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.DESIGN
NOMI_COLONNE_APP        = config.NOMI_COLONNE_APP

FLAG_SOVRASCRIVI_SHEET = True


if __name__ == "__main__":
    #DOWNLOAD FILE DAL DROPBOX
    #fase 0
    
    DROPBOX_CRED = STRUTTURA_REPOSITORY["FILE_DROPBOX_CRED"]
    DROPBOX_TOKEN = STRUTTURA_REPOSITORY["FILE_DROPBOX_TOKEN"]
    
    DROPBOX_RAW_FOLDER = STRUTTURA_DROPBOX["FOLD_RAW_TBT"]
    DROPBOX_PRC_FOLDER = STRUTTURA_DROPBOX["FOLD_PRC_TBT"]
    
    LOCAL_RAW_FOLDER = STRUTTURA_REPOSITORY["FOLD_RAW_TBT"]
    LOCAL_PRC_FOLDER = STRUTTURA_REPOSITORY["FOLD_PRC_TBT"]
    
    FOGLIO_SPESE = DESIGN["NOME_FOGLIO_SPESE"]
    FOGLIO_ENTRATE = DESIGN["NOME_FOGLIO_ENTRATE"]
    
    
    dbx = db_module.get_dropbox_client(
        dropbox_credential = DROPBOX_CRED,
        dropbox_token = DROPBOX_TOKEN
    )
    
    print("="*80)
    print(f"INIZIO FLUSSO COMPLETO: ANNO {ANNO} - MESE {MESE}")
    print(f"@ Fase 1 -- Download file dal Dropbox e salvataggio della tabella raw --")
    
    
    print("[INFO]\t Connesso al Dropbox")
    
    if FLAG_AUTO_ANNO_MESE:
        FILE_SMISTATI = db_module.smista_file_excel(
            dbx=dbx,
            dropbox_folder_destinazione=DROPBOX_RAW_FOLDER,
            dropbox_folder_origine="",
            get_raw_name=config.get_raw_name,
            estesione_files=".xlsx",
            target_broken_name="BROKEN",
            nome_colonna_data=NOMI_COLONNE_APP["COLONNE_SPESE"]["COL_SPESE_DATA"],
            righe_da_saltare=1,
            flag_sovrascrivi=True,
        )
        print(FILE_SMISTATI)
        ANNO = FILE_SMISTATI["SMISTATI"][0]["anno"]
        MESE = FILE_SMISTATI["SMISTATI"][0]["mese_str"]
    
    NAME_RAW_FILE = config.get_raw_name(anno = ANNO, mese_str = MESE)
    NAME_PROCESSED_FILE = config.get_prc_name(anno = ANNO, mese_str = MESE)
    
    RAW_DATAFRAME = db_module.get_dataframe_from_dropbox(
        dbx = dbx,
        dropbox_folder = DROPBOX_RAW_FOLDER,
        file_name = NAME_RAW_FILE
    )
    
    if isinstance(RAW_DATAFRAME, pd.DataFrame):
        print("[ERROR]\t- Non ci sono i fogli SPESE ed ENTRATE")
        raise SystemExit
    
    RAW_DATAFRAME = cast(dict[str, pd.DataFrame], RAW_DATAFRAME)
    
    if FOGLIO_SPESE not in RAW_DATAFRAME.keys():
        print(f"[ERROR]\t- Non è presente il foglio {FOGLIO_SPESE} nell'excel ")
        raise SystemExit
    
    if FOGLIO_ENTRATE not in RAW_DATAFRAME.keys():
        print(f"[ERROR]\t- Non è presente il foglio {FOGLIO_ENTRATE} nell'excel ")
        raise SystemExit 
    
    
    print("")
    
    print(f"@ Fase 2 -- Pulizia e formattazione della tabella --")
    #PROCESSA MESE
    PRC_DATAFRAME = m_module.processa_dataframe(
        df_raw=RAW_DATAFRAME,
        anno=ANNO,
        mese_str=MESE,
        design = DESIGN,
        struttura_repo = STRUTTURA_REPOSITORY,
        colonne_app = NOMI_COLONNE_APP,
        flag_blocca_se_input_manca = True, 
        flag_sovrascrivi_output = False,
        flag_stampa_percorsi = False,
        flag_stampa_duplicati = False,
        flag_processa_tutti_i_mesi = False,
        flag_stampa_spese_altro = False)
    
    
    print("[INFO]\t Pulizia e formattazione completata")
          
    print("")
    
    print(f"@ Fase 3 -- Scrittura su Google Drive --")
    
    GOOGLE_SERVICE_ACCOUNT = STRUTTURA_REPOSITORY["FILE_GOOGLE_ACCOUNT"]
    client = gd_module.get_google_client(google_service_account=GOOGLE_SERVICE_ACCOUNT)
    
    print("[INFO]\t Connesso a Google Drive")
    #SCRITTURA SU GOOGLE DRIVE
    
    #Controlla che il file spese abbia le giuste colonne:
    PRC_SPESE_DATAFRAME = PRC_DATAFRAME[FOGLIO_SPESE]

    colonne_spese_attuali = sorted(PRC_SPESE_DATAFRAME.columns)
    colonne_spese_attese = sorted([DESIGN[x] for x in NOMI_COLONNE_APP["COLONNE_SPESE"].keys()])

    if colonne_spese_attuali != colonne_spese_attese:
        print(f"[ERROR]\t- Colonne nel foglio spese:")
        print(f"\t\t colonne attuali : {colonne_spese_attuali}")
        print(f"\t\t colonne attese : {colonne_spese_attese}")
        raise ValueError 

    gd_module.sync_month_local(
        client=client,
        anno=ANNO,
        mese_str=MESE,
        df_prc=PRC_DATAFRAME,
        flag_sovrascrivi_celle=FLAG_SOVRASCRIVI_SHEET
    )
    
    db_module.upload_dataframe_to_dropbox(
        dbx = dbx,
        dropbox_folder = DROPBOX_PRC_FOLDER,
        file_name = NAME_PROCESSED_FILE,
        df = PRC_DATAFRAME,
        flag_sovrascrivi = True
    )
    
    
    print("[INFO]\t Scrittura su Google Drive completata")
    print("[INFO]\t Flusso completo terminato")
    print("="*80)
