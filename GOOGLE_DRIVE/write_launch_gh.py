import write_module as gd_module
from pathlib import Path

ANNO = "2026"
MESE = "06"

if __name__ == "__main__":
    client = gd_module.get_google_client()
    root_dir = Path(__file__).resolve().parent / "Dati" / "TabelleProcessed"

    gd_module.sync_month_local(
        client,
        ANNO,
        MESE,
        str(root_dir)
    )