## NOME FILE: MAINconfiguration.py
import pandas as pd
from dataclasses import dataclass, fields
from pathlib import Path


# ============================================================
# FUNZIONI NAMING FILE
# ============================================================

def get_raw_name(anno: str, mese_str: str) -> str: return f"app_{anno}_{mese_str}.xlsx"
def get_prc_name(anno: str, mese_str: str) -> str: return f"p_{anno}_{mese_str}.xlsx"


# ============================================================
# MESI
# ============================================================

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
    "Gennaio":   {"mese_str": "01", "nome_intero": "Gennaio",   "nome_troncato": "Gen", "numero_int": 1,  "nome_foglio_associato": "01"},
    "Febbraio":  {"mese_str": "02", "nome_intero": "Febbraio",  "nome_troncato": "Feb", "numero_int": 2,  "nome_foglio_associato": "02"},
    "Marzo":     {"mese_str": "03", "nome_intero": "Marzo",     "nome_troncato": "Mar", "numero_int": 3,  "nome_foglio_associato": "03"},
    "Aprile":    {"mese_str": "04", "nome_intero": "Aprile",    "nome_troncato": "Apr", "numero_int": 4,  "nome_foglio_associato": "04"},
    "Maggio":    {"mese_str": "05", "nome_intero": "Maggio",    "nome_troncato": "Mag", "numero_int": 5,  "nome_foglio_associato": "05"},
    "Giugno":    {"mese_str": "06", "nome_intero": "Giugno",    "nome_troncato": "Giu", "numero_int": 6,  "nome_foglio_associato": "06"},
    "Luglio":    {"mese_str": "07", "nome_intero": "Luglio",    "nome_troncato": "Lug", "numero_int": 7,  "nome_foglio_associato": "07"},
    "Agosto":    {"mese_str": "08", "nome_intero": "Agosto",    "nome_troncato": "Ago", "numero_int": 8,  "nome_foglio_associato": "08"},
    "Settembre": {"mese_str": "09", "nome_intero": "Settembre", "nome_troncato": "Set", "numero_int": 9,  "nome_foglio_associato": "09"},
    "Ottobre":   {"mese_str": "10", "nome_intero": "Ottobre",   "nome_troncato": "Ott", "numero_int": 10, "nome_foglio_associato": "10"},
    "Novembre":  {"mese_str": "11", "nome_intero": "Novembre",  "nome_troncato": "Nov", "numero_int": 11, "nome_foglio_associato": "11"},
    "Dicembre":  {"mese_str": "12", "nome_intero": "Dicembre",  "nome_troncato": "Dic", "numero_int": 12, "nome_foglio_associato": "12"},
}


# ============================================================
# STRUTTURA REPOSITORY E DROPBOX
# ============================================================

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
    "2025": "13_PYR5Whzhq0I9H8GK3-XX0_wRokNia8oM4J85kM77g",
    "2026": "18E_u3WGZUrUJIcHfoC9ylt_uJiE3XxJ7XQyQkJC85kI",
    "2027": None
}


# ============================================================
# DESIGN — Campo, CampiSpese, CampiEntrate, BETTERDesign
# ============================================================

_DESIGN_CSV = pd.read_csv(
    Path("ELABORATION/design.csv"),
    skipinitialspace=True,
    keep_default_na=False
)
_DESIGN_SPESE   = _DESIGN_CSV[_DESIGN_CSV["tipo"] == "spese"].set_index("NOME")
_DESIGN_ENTRATE = _DESIGN_CSV[_DESIGN_CSV["tipo"] == "entrate"].set_index("NOME")


class Campo:
    def __init__(self, raw: str, prc: str, sheet: str):
        self.raw   = raw
        self.prc   = prc
        self.sheet = sheet

    def __repr__(self):
        return f"Campo(raw={self.raw!r}, prc={self.prc!r}, sheet={self.sheet!r})"


@dataclass(frozen=True)
class CampiSpese:
    gruppo:    Campo = Campo(_DESIGN_SPESE["campoRAW"]["GRUPPO"],    _DESIGN_SPESE["campoPRC"]["GRUPPO"],    _DESIGN_SPESE["campoSHEET"]["GRUPPO"])
    anno:      Campo = Campo(_DESIGN_SPESE["campoRAW"]["ANNO"],      _DESIGN_SPESE["campoPRC"]["ANNO"],      _DESIGN_SPESE["campoSHEET"]["ANNO"])
    mese:      Campo = Campo(_DESIGN_SPESE["campoRAW"]["MESE"],      _DESIGN_SPESE["campoPRC"]["MESE"],      _DESIGN_SPESE["campoSHEET"]["MESE"])
    data:      Campo = Campo(_DESIGN_SPESE["campoRAW"]["DATA"],      _DESIGN_SPESE["campoPRC"]["DATA"],      _DESIGN_SPESE["campoSHEET"]["DATA"])
    categoria: Campo = Campo(_DESIGN_SPESE["campoRAW"]["CATEGORIA"], _DESIGN_SPESE["campoPRC"]["CATEGORIA"], _DESIGN_SPESE["campoSHEET"]["CATEGORIA"])
    importo:   Campo = Campo(_DESIGN_SPESE["campoRAW"]["IMPORTO"],   _DESIGN_SPESE["campoPRC"]["IMPORTO"],   _DESIGN_SPESE["campoSHEET"]["IMPORTO"])
    note:      Campo = Campo(_DESIGN_SPESE["campoRAW"]["NOTE"],      _DESIGN_SPESE["campoPRC"]["NOTE"],      _DESIGN_SPESE["campoSHEET"]["NOTE"])


@dataclass(frozen=True)
class CampiEntrate:
    anno:      Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["ANNO"],      _DESIGN_ENTRATE["campoPRC"]["ANNO"],      _DESIGN_ENTRATE["campoSHEET"]["ANNO"])
    mese:      Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["MESE"],      _DESIGN_ENTRATE["campoPRC"]["MESE"],      _DESIGN_ENTRATE["campoSHEET"]["MESE"])
    data:      Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["DATA"],      _DESIGN_ENTRATE["campoPRC"]["DATA"],      _DESIGN_ENTRATE["campoSHEET"]["DATA"])
    categoria: Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["CATEGORIA"], _DESIGN_ENTRATE["campoPRC"]["CATEGORIA"], _DESIGN_ENTRATE["campoSHEET"]["CATEGORIA"])
    importo:   Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["IMPORTO"],   _DESIGN_ENTRATE["campoPRC"]["IMPORTO"],   _DESIGN_ENTRATE["campoSHEET"]["IMPORTO"])
    note:      Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["NOTE"],      _DESIGN_ENTRATE["campoPRC"]["NOTE"],      _DESIGN_ENTRATE["campoSHEET"]["NOTE"])
    timestamp: Campo = Campo(_DESIGN_ENTRATE["campoRAW"]["TIMESTAMP"], _DESIGN_ENTRATE["campoPRC"]["TIMESTAMP"], _DESIGN_ENTRATE["campoSHEET"]["TIMESTAMP"])


@dataclass(frozen=True)
class Design:
    spese:   CampiSpese   = CampiSpese()
    entrate: CampiEntrate = CampiEntrate()

    CELLA_SPESE_FIRST_ENTRY:    str = "B1"
    CELLA_SPESE_TSTAMP:         str = "J1"
    CELLA_ENTRATE_FIRST_ENTRY:  str = "A1"

    NOME_FOGLIO_SPESE:          str = "Spese"
    NOME_FOGLIO_ENTRATE:        str = "Entrate"
    NOME_FOGLIO_TOTAL_SPESE:    str = "TOTAL_spese"
    NOME_FOGLIO_TOTAL_ENTRATE:  str = "TOTAL_entrate"
    NOME_FILE_ROTTO:            str = "BROKEN"

    # ---- SPESE ----
    @classmethod
    def map_spese_RAWtoPRC(cls) -> dict[str, str]:
        return {getattr(cls.spese, f.name).raw: getattr(cls.spese, f.name).prc
                for f in fields(CampiSpese) if getattr(cls.spese, f.name).raw != ""}

    @classmethod
    def colonne_spese_RAW(cls) -> list[str]:
        return [getattr(cls.spese, f.name).raw for f in fields(CampiSpese) if getattr(cls.spese, f.name).raw != ""]

    @classmethod
    def num_col_spese_RAW(cls) -> int:
        return len(cls.colonne_spese_RAW())

    @classmethod
    def colonne_spese_PRC(cls) -> list[str]:
        return [getattr(cls.spese, f.name).prc for f in fields(CampiSpese) if getattr(cls.spese, f.name).prc != ""]

    @classmethod
    def num_col_spese_PRC(cls) -> int:
        return len(cls.colonne_spese_PRC())

    @classmethod
    def colonne_spese_SHEET(cls) -> list[str]:
        return [getattr(cls.spese, f.name).sheet for f in fields(CampiSpese) if getattr(cls.spese, f.name).sheet != ""]

    @classmethod
    def num_col_spese_SHEET(cls) -> int:
        return len(cls.colonne_spese_SHEET())

    # ---- ENTRATE ----
    @classmethod
    def map_entrate_RAWtoPRC(cls) -> dict[str, str]:
        return {getattr(cls.entrate, f.name).raw: getattr(cls.entrate, f.name).prc
                for f in fields(CampiEntrate) if getattr(cls.entrate, f.name).raw != ""}

    @classmethod
    def colonne_entrate_RAW(cls) -> list[str]:
        return [getattr(cls.entrate, f.name).raw for f in fields(CampiEntrate) if getattr(cls.entrate, f.name).raw != ""]

    @classmethod
    def num_col_entrate_RAW(cls) -> int:
        return len(cls.colonne_entrate_RAW())

    @classmethod
    def colonne_entrate_PRC(cls) -> list[str]:
        return [getattr(cls.entrate, f.name).prc for f in fields(CampiEntrate) if getattr(cls.entrate, f.name).prc != ""]

    @classmethod
    def num_col_entrate_PRC(cls) -> int:
        return len(cls.colonne_entrate_PRC())

    @classmethod
    def colonne_entrate_SHEET(cls) -> list[str]:
        return [getattr(cls.entrate, f.name).sheet for f in fields(CampiEntrate) if getattr(cls.entrate, f.name).sheet != ""]

    @classmethod
    def num_col_entrate_SHEET(cls) -> int:
        return len(cls.colonne_entrate_SHEET())

