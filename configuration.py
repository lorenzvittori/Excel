## NOME FILE: configuration.py
from dataclasses import dataclass
from pathlib import Path


def get_raw_name(anno: str, mese_str: str): return f"app_{anno}_{mese_str}.xlsx"
def get_prc_name(anno: str, mese_str: str): return f"p_{anno}_{mese_str}.xlsx"


MESI = {
    # Accesso tramite numero
    "01": {"mese_str": "01", "nome_intero": "Gennaio",   "nome_troncato": "Gen", "numero_int": 1,  "nome_foglio_associato": "01"},
    "02": {"mese_str": "02", "nome_intero": "Febbraio",  "nome_troncato": "Feb", "numero_int": 2,  "nome_foglio_associato": "02"},
    "03": {"mese_str": "03", "nome_intero": "Marzo",     "nome_troncato": "Mar", "numero_int": 3,  "nome_foglio_associato": "03"},
    "04": {"mese_str": "04", "nome_intero": "Aprile",    "nome_troncato": "Apr", "numero_int": 4,  "nome_foglio_associato": "04"},
    "05": {"mese_str": "05", "nome_intero": "Maggio",    "nome_troncato": "Mag", "numero_int": 5,  "nome_foglio_associato": "05"},
    "06": {"mese_str": "06", "nome_intero": "Giugno",    "nome_troncato": "Giu", "numero_int": 6,  "nome_foglio_associato": "06"},
    "07": {"mese_str": "07", "nome_intero": "Luglio",    "nome_troncato": "Lug", "numero_int": 7,  "nome_foglio_associato": "07"},
    "08": {"mese_str": "08", "nome_intero": "Agosto",    "nome_troncato": "Ago", "numero_int": 8,  "nome_foglio_associato": "08"},
    "09": {"mese_str": "09", "nome_intero": "Settembre", "nome_troncato": "Set", "numero_int": 9,  "nome_foglio_associato": "09"},
    "10": {"mese_str": "10", "nome_intero": "Ottobre",   "nome_troncato": "Ott", "numero_int": 10, "nome_foglio_associato": "10"},
    "11": {"mese_str": "11", "nome_intero": "Novembre",  "nome_troncato": "Nov", "numero_int": 11, "nome_foglio_associato": "11"},
    "12": {"mese_str": "12", "nome_intero": "Dicembre",  "nome_troncato": "Dic", "numero_int": 12, "nome_foglio_associato": "12"},

    # Accesso tramite nome intero
    "Gennaio":   {"nome_intero": "Gennaio",  "mese_str": "01", "nome_troncato": "Gen", "numero_int": 1,  "nome_foglio_associato": "01"},
    "Febbraio":  {"nome_intero": "Febbraio", "mese_str": "02", "nome_troncato": "Feb", "numero_int": 2,  "nome_foglio_associato": "02"},
    "Marzo":     {"nome_intero": "Marzo",    "mese_str": "03", "nome_troncato": "Mar", "numero_int": 3,  "nome_foglio_associato": "03"},
    "Aprile":    {"nome_intero": "Aprile",   "mese_str": "04", "nome_troncato": "Apr", "numero_int": 4,  "nome_foglio_associato": "04"},
    "Maggio":    {"nome_intero": "Maggio",   "mese_str": "05", "nome_troncato": "Mag", "numero_int": 5,  "nome_foglio_associato": "05"},
    "Giugno":    {"nome_intero": "Giugno",   "mese_str": "06", "nome_troncato": "Giu", "numero_int": 6,  "nome_foglio_associato": "06"},
    "Luglio":    {"nome_intero": "Luglio",   "mese_str": "07", "nome_troncato": "Lug", "numero_int": 7,  "nome_foglio_associato": "07"},
    "Agosto":    {"nome_intero": "Agosto",   "mese_str": "08", "nome_troncato": "Ago", "numero_int": 8,  "nome_foglio_associato": "08"},
    "Settembre": {"nome_intero": "Settembre","mese_str": "09", "nome_troncato": "Set", "numero_int": 9,  "nome_foglio_associato": "09"},
    "Ottobre":   {"nome_intero": "Ottobre",  "mese_str": "10", "nome_troncato": "Ott", "numero_int": 10, "nome_foglio_associato": "10"},
    "Novembre":  {"nome_intero": "Novembre", "mese_str": "11", "nome_troncato": "Nov", "numero_int": 11, "nome_foglio_associato": "11"},
    "Dicembre":  {"nome_intero": "Dicembre", "mese_str": "12", "nome_troncato": "Dic", "numero_int": 12, "nome_foglio_associato": "12"},
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
    "2024": "1mcYYhh4VEkwVlQ6SoqcubClws61QEi08kPlY5ik5liQ",
    "2025": "13_PYR5Whzhq0I9H8GK3-XX0_wRokNia8oM4J85kM77g", #"1A8pxVxMtFhDRcISgSJBKETwfeFh1hRfrYp6mO0kNmgs",
    "2026": "18E_u3WGZUrUJIcHfoC9ylt_uJiE3XxJ7XQyQkJC85kI",
    "2027": None
}

# ----------------------------------------- DESIGN -----------------------------------------

@dataclass(frozen=True)
class Design:
    COL_SPESE_ANNO: str         = "Anno"
    COL_SPESE_MESE: str         = "Mese"
    COL_SPESE_DATA: str         = "Data"
    COL_SPESE_CATEGORIA: str    = "Categoria"
    COL_SPESE_IMPORTO: str      = "Importo"
    COL_SPESE_NOTE: str         = "Note"

    COL_ENTRATE_ANNO: str       = "Anno"
    COL_ENTRATE_MESE: str       = "Mese"
    COL_ENTRATE_DATA: str       = "Data"
    COL_ENTRATE_CATEGORIA: str  = "Categoria"
    COL_ENTRATE_IMPORTO: str    = "Importo"
    COL_ENTRATE_NOTE: str       = "Note"
    COL_ENTRATE_TSTAMP: str     = "TimeStamp"
    
    CELLA_SPESE_FIRST_ENTRY: str    = "B1"
    CELLA_SPESE_TSTAMP: str         = "J1"
    CELLA_ENTRATE_FIRST_ENTRY: str  = "A1"

    NOME_FOGLIO_SPESE: str      = "Spese"
    NOME_FOGLIO_ENTRATE: str    = "Entrate"

    NOME_FOGLIO_TOTAL_SPESE: str    = "TOTAL_spese"
    NOME_FOGLIO_TOTAL_ENTRATE: str  = "TOTAL_entrate"
    NOME_FILE_ROTTO: str        = "BROKEN"
    
    @classmethod
    def colonne_sheet_spese(cls):
        return [
            getattr(cls, x)
            for x in vars(cls)
            if x.startswith("COL_SPESE")
        ]
    
    @classmethod
    def colonne_sheet_entrate(cls):
        return [
            getattr(cls, x)
            for x in vars(cls)
            if x.startswith("COL_ENTRATE")
        ]
        
    @classmethod
    def num_col_sheet_spese(cls):
        return len(cls.colonne_sheet_spese())

    @classmethod
    def num_col_sheet_entrate(cls):
        return len(cls.colonne_sheet_entrate())


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



