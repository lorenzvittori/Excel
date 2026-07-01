import dropbox_module as db_module
from pathlib import Path


ANNO = "2026"
MESE = "06"

file_name = f"app_{ANNO}_{MESE}.xlsx"

if __name__ == "__main__":
    db_module.download_file_from_dropbox(
        Path("Dati/TabelleApp"),
        file_name,
        blocca_se_esistente=True
    )
