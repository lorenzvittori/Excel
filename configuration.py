## NOME FILE: configuration.py
#FORMATO DEI NOMI DEI FILE DI INPUT E OUTPUT
from pathlib import Path


def get_raw_name(anno: str, mese_str: str): return f"app_{anno}_{mese_str}.xlsx"
def get_prc_name(anno: str, mese_str: str): return f"p_{anno}_{mese_str}.xlsx"


MESI = {
    "01": {"nome_intero": "Gennaio",    "nome_troncato": "Gen", "numero_int": 1,    "nome_foglio_associato": "01"},
    "02": {"nome_intero": "Febbraio",   "nome_troncato": "Feb", "numero_int": 2,    "nome_foglio_associato": "02"},
    "03": {"nome_intero": "Marzo",      "nome_troncato": "Mar", "numero_int": 3,    "nome_foglio_associato": "03"},
    "04": {"nome_intero": "Aprile",     "nome_troncato": "Apr", "numero_int": 4,    "nome_foglio_associato": "04"},
    "05": {"nome_intero": "Maggio",     "nome_troncato": "Mag", "numero_int": 5,    "nome_foglio_associato": "05"},
    "06": {"nome_intero": "Giugno",     "nome_troncato": "Giu", "numero_int": 6,    "nome_foglio_associato": "06"},
    "07": {"nome_intero": "Luglio",     "nome_troncato": "Lug", "numero_int": 7,    "nome_foglio_associato": "07"},
    "08": {"nome_intero": "Agosto",     "nome_troncato": "Ago", "numero_int": 8,    "nome_foglio_associato": "08"},
    "09": {"nome_intero": "Settembre",  "nome_troncato": "Set", "numero_int": 9,    "nome_foglio_associato": "09"},
    "10": {"nome_intero": "Ottobre",    "nome_troncato": "Ott", "numero_int": 10,   "nome_foglio_associato": "10"},
    "11": {"nome_intero": "Novembre",   "nome_troncato": "Nov", "numero_int": 11,   "nome_foglio_associato": "11"},
    "12": {"nome_intero": "Dicembre",   "nome_troncato": "Dic", "numero_int": 12,   "nome_foglio_associato": "12"},
}


# ------------------------------------- CONFIGURAZIONE -------------------------------------
STRUTTURA_REPOSITORY = {
    "FOLD_DATI":            Path("ELABORATION"),
    "FILE_ADD_ROWS":        Path("ELABORATION/additional_rows.csv"),
    "FOLD_DROPBOX":         Path("DROPBOX"),
    "FILE_DROPBOX_CRED":    Path("DROPBOX/dropbox_credentials.json"),
    "FILE_DROPBOX_TOKEN":   Path("DROPBOX/dropbox_token.json"),
    "FOLD_GOOGLE":          Path("GOOGLE_DRIVE"),
    "FILE_GOOGLE_ACCOUNT":  Path("GOOGLE_DRIVE/google_service_account.json")
}

STRUTTURA_DROPBOX = {
    "FOLD_TO_SORT":     "",
    "FOLD_RAW_TBT":     "/sheets_RAW",
    "FOLD_PRC_TBT":     "/sheets_PROCESSED"
}

ID_GOOGLE_SHEET = {
    "2024": "1Z0PgcNWeSMP5adDeG-Wsj5YpgbXK-V3-I3BQrb8a4jE",
    "2025": "13_PYR5Whzhq0I9H8GK3-XX0_wRokNia8oM4J85kM77g", #"1A8pxVxMtFhDRcISgSJBKETwfeFh1hRfrYp6mO0kNmgs",
    "2026": "18E_u3WGZUrUJIcHfoC9ylt_uJiE3XxJ7XQyQkJC85kI",
    "2027": None
}

# ----------------------------------------- DESIGN -----------------------------------------

DESIGN = {
    "COL_SPESE_ANNO":           "Anno",
    "COL_SPESE_MESE":           "Mese",
    "COL_SPESE_DATA":           "Data",
    "COL_SPESE_CATEGORIA":      "Categoria",
    "COL_SPESE_IMPORTO":        "Importo",
    "COL_SPESE_NOTE":           "Note",
    
    "COL_ENTRATE_ANNO":         "Anno",
    "COL_ENTRATE_MESE":         "Mese",
    "COL_ENTRATE_DATA":         "Data",
    "COL_ENTRATE_CATEGORIA":    "Categoria",
    "COL_ENTRATE_IMPORTO":      "Importo",
    "COL_ENTRATE_NOTE":         "Note",
    
    "NOME_FOGLIO_SPESE":        "Spese",
    "NOME_FOGLIO_ENTRATE":      "Entrate",
    
    "NOME_FOGLIO_TOTAL_ENTRATE": "TOTAL_entrate",
    "NOME_FILE_ROTTO":          "BROKEN"        #Nome del file da smistare che non ha unici (anno, mese)
}

NUMERO_COLONNE_SHEET_SPESE      = sum(1 for x in DESIGN.keys() if x.startswith("COL_SPESE"))
NUMERO_COLONNE_SHEET_ENTRATE    = sum(1 for x in DESIGN.keys() if x.startswith("COL_ENTRATE"))

NOMI_COLONNE_APP = {
    "COLONNE_SPESE": {
        "COL_SPESE_DATA":           "Data e ora",
        "COL_SPESE_CATEGORIA":      "Categoria",
        "COL_SPESE_IMPORTO":        "Importo in valuta del conto",
        "COL_SPESE_NOTE":           "Commento",
    },
    "COLONNE_ENTRATE": {
        "COL_ENTRATE_DATA":         "Data e ora",
        "COL_ENTRATE_CATEGORIA":    "Categoria",
        "COL_ENTRATE_IMPORTO":      "Importo in valuta del conto",
        "COL_ENTRATE_NOTE":         "Commento",
    }
}



