#NOME MODULO: logger.py
import sys
sys.stdout.reconfigure(encoding='utf-8')        #type: ignore

_contatore_fase = 0
_profondita = 0
_flag_riga_vuota = False
BLOCK_LENGTH = 46
BULLET_PHASE = "• "
BULLET_MEX = ""

def linea() -> None:
    print("-" * BLOCK_LENGTH)

def separatore() -> None:
    print("=" * BLOCK_LENGTH)

def get_tab(n: int) -> str:
    return "   " * n

def end_all_phases() -> None:
    global _profondita, _flag_riga_vuota
    _profondita = 0
    if not(_flag_riga_vuota):
        _flag_riga_vuota = True
        print("")

def new_phase(corpo: str) -> None:
    global _contatore_fase, _profondita, _flag_riga_vuota
    if not(_flag_riga_vuota):
        _flag_riga_vuota = True
        print("")
    corpo = corpo.strip()

    if _profondita == 0:
        _contatore_fase += 1
        print(f"Fase {_contatore_fase}: {corpo}")
    else:
        print(f"{get_tab(_profondita)}{BULLET_PHASE}{corpo}:")

    _profondita += 1


def end_phase() -> None:
    global _profondita, _flag_riga_vuota
    _profondita = max(0, _profondita - 1)
    if not(_flag_riga_vuota):
        _flag_riga_vuota = True
        print("")


def ok_mex(corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("OK", corpo=corpo, dettaglio=dettaglio)


def info_mex(corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("INFO", corpo=corpo, dettaglio=dettaglio)


def error_mex(corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("ERROR", corpo=corpo, dettaglio=dettaglio)


def warning_mex(corpo: str, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("WARNING", corpo=corpo, dettaglio=dettaglio)


def tipo_messaggio(tipo: str, corpo: str, dettaglio: str | list[str] | None = None) -> None:
    global _flag_riga_vuota
    _flag_riga_vuota = False
    tipo = tipo.strip()
    corpo = corpo.strip()
    print(f"{get_tab(_profondita)}{BULLET_MEX}[{tipo}]: {corpo}")

    if dettaglio is None:
        return

    if isinstance(dettaglio, str):
        dettaglio = [dettaglio]

    for mex in dettaglio:
        mex = mex.strip()
        if mex:
            print(f"{get_tab(_profondita + 2)}{mex}")


def reset_fase(valore_iniziale: int = 0) -> None:
    global _contatore_fase, _profondita
    _contatore_fase = valore_iniziale
    _profondita = 0