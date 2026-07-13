import pandas as pd
from dataclasses import dataclass
from dataclasses import fields

# ---- Carica il CSV una volta sola ----
_DESIGN   = pd.read_csv("design.csv", skipinitialspace=True)
_DESIGN_ENTRATE = _DESIGN[_DESIGN["tipo"] == "entrate"].set_index("NOME")
_DESIGN_SPESE   = _DESIGN[_DESIGN["tipo"] == "spese"].set_index("NOME")

class Campo:
    def __init__(self, app: str | None, sheet: str | None):
        self.app   = app
        self.sheet = sheet

    def __repr__(self):
        return f"Campo(app={self.app!r}, sheet={self.sheet!r})"

@dataclass(frozen=True)
class CampiSpese:
    gruppo:    Campo = Campo(_DESIGN_SPESE["campoAPP"]["GRUPPO"],    _DESIGN_SPESE["campoSHEET"]["GRUPPO"])
    anno:      Campo = Campo(_DESIGN_SPESE["campoAPP"]["ANNO"],      _DESIGN_SPESE["campoSHEET"]["ANNO"])
    mese:      Campo = Campo(_DESIGN_SPESE["campoAPP"]["MESE"],      _DESIGN_SPESE["campoSHEET"]["MESE"])
    data:      Campo = Campo(_DESIGN_SPESE["campoAPP"]["DATA"],      _DESIGN_SPESE["campoSHEET"]["DATA"])
    categoria: Campo = Campo(_DESIGN_SPESE["campoAPP"]["CATEGORIA"], _DESIGN_SPESE["campoSHEET"]["CATEGORIA"])
    importo:   Campo = Campo(_DESIGN_SPESE["campoAPP"]["IMPORTO"],   _DESIGN_SPESE["campoSHEET"]["IMPORTO"])
    note:      Campo = Campo(_DESIGN_SPESE["campoAPP"]["NOTE"],      _DESIGN_SPESE["campoSHEET"]["NOTE"])

@dataclass(frozen=True)
class CampiEntrate:
    anno:      Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["ANNO"],      _DESIGN_ENTRATE["campoSHEET"]["ANNO"])
    mese:      Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["MESE"],      _DESIGN_ENTRATE["campoSHEET"]["MESE"])
    data:      Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["DATA"],      _DESIGN_ENTRATE["campoSHEET"]["DATA"])
    categoria: Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["CATEGORIA"], _DESIGN_ENTRATE["campoSHEET"]["CATEGORIA"])
    importo:   Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["IMPORTO"],   _DESIGN_ENTRATE["campoSHEET"]["IMPORTO"])
    note:      Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["NOTE"],      _DESIGN_ENTRATE["campoSHEET"]["NOTE"])
    timestamp: Campo = Campo(_DESIGN_ENTRATE["campoAPP"]["TIMESTAMP"], _DESIGN_ENTRATE["campoSHEET"]["TIMESTAMP"])

@dataclass(frozen=True)
class BETTERDesign:
    spese:   CampiSpese   = CampiSpese()
    entrate: CampiEntrate = CampiEntrate()
    
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
        return [getattr(cls.spese, f.name).sheet for f in fields(CampiSpese)]
    
    @classmethod
    def colonne_sheet_entrate(cls):
        return [getattr(cls.entrate, f.name).sheet for f in fields(CampiEntrate)]
        
    @classmethod
    def num_col_sheet_spese(cls):
        return len(cls.colonne_sheet_spese())

    @classmethod
    def num_col_sheet_entrate(cls):
        return len(cls.colonne_sheet_entrate())
    




