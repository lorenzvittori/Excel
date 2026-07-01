from DROPBOX import dropbox_module as db_module
from GOOGLE_DRIVE import write_module as gd_module
import main_module as m_module
import configuration as config  
from pathlib import Path
import pandas as pd


ANNO = "2026"
MESE = "06"

if __name__ == "__main__":
    # ---- DROPBOX -----
    file_name = f"app_{ANNO}_{MESE}.xlsx"
    root_dir = Path("Dati/TabelleApp")
    
    db_module.download_file_from_dropbox(
        download_folder=root_dir,
        file_name=file_name,
        blocca_se_esistente=False
    )
    
    m_module.processa_mese(
        anno=ANNO,
        mese_numb=MESE,
        design = config.DESIGN,
        structure =config.STRUTTURA_DATI,
        colonne_app = config.NOMI_COLONNE_APP,
        flag_blocca_se_input_manca = True, 
        flag_sovrascrivi_output = False,
        flag_stampa_percorsi = False,
        flag_stampa_duplicati = False,
        flag_processa_tutti_i_mesi = False,
        flag_stampa_spese_altro = False)
    
    
    client = gd_module.get_google_client()
    
    root_dir = m_module.prepara_percorsi(
        anno=ANNO,
        mese_numb=MESE,
        structure=config.STRUTTURA_DATI,
        flag_blocca_se_input_manca=True,
        flag_sovrascrivi_output=False
    )
    root_dir = Path(root_dir["output_file"]).parent

    gd_module.sync_month_local(
        client =client,
        anno = ANNO,
        mese = MESE,
        base_path = str(root_dir)
    )

