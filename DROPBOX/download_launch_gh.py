import dropbox_module as db_module
from pathlib import Path

ANNO = "2026"
MESE = "06"

if __name__ == "__main__":
    file_name = f"app_{ANNO}_{MESE}.xlsx"
    root_dir = Path("Dati/TabelleProcessed")
    
    db_module.download_file_from_dropbox(
        root_dir,
        file_name,
        blocca_se_esistente=True
    )
