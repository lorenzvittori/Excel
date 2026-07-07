#NOME MODULO: logger.py

BLOCK_LENGTH = 46
_contatore_fase = 0
_contatore_sottofase = 0

def separatore() -> None:
    print("=" * BLOCK_LENGTH)

def start(corpo: str) -> None:
    print("\n")
    separatore()
    print(corpo)
    print("\n")
    
    
def inizio_flusso_anno_mese(anno:str, mese_str:str) ->None:
    print(f"INIZIO FLUSSO: ANNO {anno} - MESE {mese_str}")


def inizio_istanza(corpo:str) -> None:
    print(f"{corpo}...", end = "")


def fine_istanza() -> None:
    print("\tOK")

def sottofase(corpo: str) -> None:
    global _contatore_sottofase
    _contatore_sottofase += 1
    print(f"\t- SottoFase {_contatore_sottofase} - {corpo}")


def reset_fase() -> None:
    """Resetta il contatore delle fasi, utile a inizio script o tra run diversi."""
    global _contatore_fase
    global _contatore_sottofase
    _contatore_fase = 0
    _contatore_sottofase = 0

def fine(anno:str, mese_str:str) ->None:
    print(f"FLUSSO {anno}-{mese_str} COMPLETATO")

def fase(corpo: str) -> None:
    global _contatore_fase
    global _contatore_sottofase
    _contatore_sottofase = 0
    _contatore_fase += 1
    print(f"@ Fase {_contatore_fase} - {corpo}")
    
    
def tipo_messaggio(tipo: str, corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo = tipo.strip()
    corpo = corpo.strip()
    print(f"[{tipo}]\t - {corpo}")

    if dettaglio is None:
        return

    if isinstance(dettaglio, str):
        dettaglio = [dettaglio]

    for mex in dettaglio:
        mex = mex.strip()
        if mex:  # salta eventuali stringhe vuote nella lista
            print(f"\t\t{mex}")