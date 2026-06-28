import dropbox
from pathlib import Path

#Constanti
def download_file_from_dropbox(download_folder: Path, file_name: str, blocca_se_esistente: bool = True):
    TOKEN_FILE = "token_dropbox.txt"
    DROPBOX_FOLDER = "/TabelleApp"

    # ---- TOKEN -----
    BASE_DIR = Path(__file__).resolve().parent
    TOKEN_FILE_DIR = BASE_DIR / TOKEN_FILE
    TOKEN = TOKEN_FILE_DIR.read_text().strip()
    dbx = dropbox.Dropbox(TOKEN)
    
    # ---- DIRECTORY -----
    OUTPUT_DIR = download_folder / file_name
    DROPBOX_DIR = f"{DROPBOX_FOLDER}/{file_name}"


    # ---- CHECK -----
    try:
        dbx.files_get_metadata(DROPBOX_DIR)
    except dropbox.exceptions.ApiError: 
        print("-!- FILE NON PRESENTE SU DROPBOX: ...", end="")
        print(DROPBOX_DIR)
        print("Processo terminato, sono presenti i seguenti file:")
        for f in dbx.files_list_folder(DROPBOX_FOLDER).entries:
            print(f"  - {f.name}")
        raise SystemExit
    
    
    if not download_folder.exists():
        print("Cartella di destinazione non esistente")
        raise SystemExit

    if Path(OUTPUT_DIR).exists():
        print("-!- File già esistente nella cartella di destinazione", end ="")
        if blocca_se_esistente:
            print(" -> Download interrotto")
            raise SystemExit
        else:
            print(" -> File sovrascritto")

    # ---- DOWNLOAD -----
    dbx.files_download_to_file(str(OUTPUT_DIR), str(DROPBOX_DIR))

    print("Download completato:", OUTPUT_DIR)
    
    
    


output_folder = Path(__file__).resolve().parent / "Dati" / "TabelleApp"
download_file_from_dropbox(output_folder, "app_2026_06.xlsx", blocca_se_esistente=True)
    