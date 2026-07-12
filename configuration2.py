import pandas as pd
from dataclasses import dataclass

# Definizioni delle classi (già fornite)
@dataclass(frozen=True)
class Campo:
    app: str | None
    sheet: str | None
    ordine_app: int | None
    ordine_sheet: int | None

@dataclass(frozen=True)
class CampiSpese:
    GRUPPO: Campo
    ANNO: Campo
    MESE: Campo
    DATA: Campo
    CATEGORIA: Campo
    IMPORTO: Campo
    NOTE: Campo

@dataclass(frozen=True)
class CampiEntrate:
    ANNO: Campo
    MESE: Campo
    DATA: Campo
    CATEGORIA: Campo
    IMPORTO: Campo
    NOTE: Campo
    TIMESTAMP: Campo

@dataclass(frozen=True)
class Design:
    spese: CampiSpese
    entrate: CampiEntrate

# -------------------------------------------
# Lettura e popolamento a partire da design.csv
# -------------------------------------------

def carica_design(csv_path: str) -> Design:
    df = pd.read_csv(csv_path)

    def crea_campo(row) -> Campo:
        app = row['campoAPP'] if pd.notna(row['campoAPP']) else None
        sheet = row['campoSHEET'] if pd.notna(row['campoSHEET']) else None
        ordine_app = int(row['ordineAPP']) if pd.notna(row['ordineAPP']) else None
        ordine_sheet = int(row['ordineSHEET']) if pd.notna(row['ordineSHEET']) else None
        return Campo(app=app, sheet=sheet, ordine_app=ordine_app, ordine_sheet=ordine_sheet)

    spese = {}
    entrate = {}

    for _, row in df.iterrows():
        nome = row['NOME']
        tipo = row['tipo']
        campo = crea_campo(row)
        if tipo == 'spese':
            spese[nome] = campo
        elif tipo == 'entrate':
            entrate[nome] = campo

    # Costruzione dei sottogruppi
    campi_spese = CampiSpese(
        GRUPPO=spese['GRUPPO'],
        ANNO=spese['ANNO'],
        MESE=spese['MESE'],
        DATA=spese['DATA'],
        CATEGORIA=spese['CATEGORIA'],
        IMPORTO=spese['IMPORTO'],
        NOTE=spese['NOTE']
    )

    campi_entrate = CampiEntrate(
        ANNO=entrate['ANNO'],
        MESE=entrate['MESE'],
        DATA=entrate['DATA'],
        CATEGORIA=entrate['CATEGORIA'],
        IMPORTO=entrate['IMPORTO'],
        NOTE=entrate['NOTE'],
        TIMESTAMP=entrate['TIMESTAMP']
    )

    return Design(spese=campi_spese, entrate=campi_entrate)

# Esempio di utilizzo
design = carica_design('design.csv')
print(design.entrate.IMPORTO.app)