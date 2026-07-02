## NOME FILE: FLUSSO_TOTALE.py
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
    db_module.download_file_from_dropbox(
        anno = ANNO,
        mese_str = MESE,
        struttura_repo=STRUTTURA_REPOSITORY,
        struttura_dbox=STRUTTURA_DROPBOX,
        blocca_se_esistente=False
    )
    
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
    
    #SCRITTURA SU GOOGLE DRIVE
    gd_module.sync_month_local(
        anno = ANNO,
        mese_str = MESE,
        struttura_repo = STRUTTURA_REPOSITORY)

