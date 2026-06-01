from pathlib import Path
import os
import gdown

# =========================
# PARAMETRI DA MODIFICARE
# =========================
MESE = "Maggio"
YY = "26"

FOLDER_URL = "https://drive.google.com/drive/folders/1DFf83wYh1ZGDZ8ChZqbuVNSAD3t1bnfg?usp=drive_link"
SOURCE_FILENAME = "2026_06_01_16_08_43_563370.xlsx"

OUTPUT_FILENAME = f"app_{MESE}{YY}.xlsx"

# =========================
# PERCORSI LOCALI
# =========================

# Cartella dove si trova questo script: Excel/
BASE_DIR = Path(__file__).resolve().parent

# Cartella finale: Excel/Dati/TabelleApp/
DEST_DIR = BASE_DIR / "Dati" / "TabelleApp"
DEST_DIR.mkdir(parents=True, exist_ok=True)

# File finale
DEST_FILE = DEST_DIR / OUTPUT_FILENAME

# Cartella temporanea per scaricare la cartella Drive
TEMP_DIR = BASE_DIR / "_temp_drive_download"
TEMP_DIR.mkdir(exist_ok=True)

print("Scaricamento dalla cartella Google Drive...")

downloaded_files = gdown.download_folder(
    url=FOLDER_URL,
    output=str(TEMP_DIR),
    quiet=False,
    use_cookies=False
)

if not downloaded_files:
    raise RuntimeError(
        "Nessun file scaricato. Controlla che la cartella Google Drive sia accessibile tramite link."
    )

source_path = None

for file_path in downloaded_files:
    file_path = Path(file_path)

    if file_path.name == SOURCE_FILENAME:
        source_path = file_path
        break

if source_path is None:
    raise FileNotFoundError(
        f"File non trovato nella cartella Drive: {SOURCE_FILENAME}"
    )

# Se esiste già un file con lo stesso nome, viene sovrascritto
if DEST_FILE.exists():
    DEST_FILE.unlink()

source_path.rename(DEST_FILE)

# Pulizia: elimina gli altri file temporanei scaricati
for file_path in TEMP_DIR.rglob("*"):
    if file_path.is_file():
        try:
            file_path.unlink()
        except OSError:
            pass

try:
    TEMP_DIR.rmdir()
except OSError:
    pass

print("File scaricato e salvato correttamente:")
print(DEST_FILE)