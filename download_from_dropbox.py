import dropbox
import os

# -----------------------
# CONFIG
# -----------------------
DROPBOX_TOKEN = os.environ["DROPBOX_TOKEN"]

FILE_NAME = "app_2026_06.xlsx"
DROPBOX_PATH = f"/Finanze/{FILE_NAME}"   # cambia cartella se serve
LOCAL_PATH = f"data/raw/{FILE_NAME}"

# -----------------------
# CLIENT
# -----------------------
dbx = dropbox.Dropbox(DROPBOX_TOKEN)

# -----------------------
# DOWNLOAD
# -----------------------
os.makedirs("data/raw", exist_ok=True)

try:
    dbx.files_download_to_file(LOCAL_PATH, DROPBOX_PATH)
    print(f"Download completato: {LOCAL_PATH}")

except Exception as e:
    print("Errore download:", e)