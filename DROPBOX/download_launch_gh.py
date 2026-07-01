import dropbox_module as dropbox_utils
from pathlib import Path


ANNO = "2026"
MESE = "06"

file_name = f"app_{ANNO}_{MESE}.xlsx"

if __name__ == "__main__":
    dropbox_utils.download_file_from_dropbox(
        Path("Dati/TabelleApp"),
        file_name,
        blocca_se_esistente=True
    )
