## NOME FILE: FLUSSO_TOTALE.py
from time import time

from DROPBOX import dropbox_module as db_module
from GOOGLE_DRIVE import write_module as gd_module
import main_module as m_module
import configuration as config  
from pathlib import Path
import pandas as pd


ANNO = "2026"
MESE = "06"
STRUTTURA_REPOSITORY    = config.STRUTTURA_REPOSITORY
STRUTTURA_DROPBOX       = config.STRUTTURA_DROPBOX
DESIGN                  = config.DESIGN
NOMI_COLONNE_APP        = config.NOMI_COLONNE_APP


if __name__ == "__main__":
    #DOWNLOAD FILE DAL DROPBOX
    print("="*80)
    print(f"INIZIO FLUSSO COMPLETO: ANNO {ANNO} - MESE {MESE}")
    print(f"@ Fase 1 -- Download file dal Dropbox e salvataggio della tabella raw --")
    
    dbx = db_module.get_dropbox_client(struttura_repo=STRUTTURA_REPOSITORY)
    print("[INFO] \t Connesso al Dropbox")
    
    db_module.download_file_from_dropbox(
        dbx = dbx,
        anno = ANNO,
        mese_str = MESE,
        struttura_repo=STRUTTURA_REPOSITORY,
        struttura_dbox=STRUTTURA_DROPBOX,
        blocca_se_esistente=False
    )
    print("[INFO] \t Download completato")
    
    print("")
    
    print(f"@ Fase 2 -- Pulizia e formattazione della tabella --")
    #PROCESSA MESE
    m_module.processa_mese(
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
    
    print("[INFO] \t Pulizia e formattazione completata")
          
    print("")
    
    print(f"@ Fase 3 -- Scrittura su Google Drive --")
    
    client = gd_module.get_google_client(struttura_repo=STRUTTURA_REPOSITORY)
    print("[INFO] \t Connesso a Google Drive")
    #SCRITTURA SU GOOGLE DRIVE

    gd_module.sync_month_local(
        client = client,
        anno = ANNO,
        mese_str = MESE,
        struttura_repo = STRUTTURA_REPOSITORY,
        flag_sovrascrivi_celle = True
        )
    print("[INFO] \t Scrittura su Google Drive completata")
    print("[INFO] \t Flusso completo terminato")
    print("="*80)
