import dropbox_module as dropbox_utils
from pathlib import Path

if __name__ == "__main__":
    dropbox_utils.download_file_from_dropbox(
        Path("Dati/TabelleApp"),
        "app_2026_06.xlsx",
        blocca_se_esistente=True
    )
