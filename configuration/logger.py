#NOME MODULO: logger.py
import sys
from pathlib import Path
from datetime import datetime
from tabulate import tabulate
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')        #type: ignore

_contatore_fase = 0
_profondita = 0
_flag_riga_vuota = False
BLOCK_LENGTH = 60
BULLET_PHASE = "• "
BULLET_MEX = ""
INDENTAZIONE = "   "

# ============================================================
# REPORT — buffer che accumula tutto ciò che viene "stampato"
# ============================================================

_REPORT_LINES: list[str] = []
_FLAG_STAMPA_TERMINALE = True   # se False: il report viene comunque accumulato ma non stampato


def set_stampa_terminale(flag: bool) -> None:
    """Abilita/disabilita la stampa a terminale. Il report viene sempre accumulato comunque."""
    global _FLAG_STAMPA_TERMINALE
    _FLAG_STAMPA_TERMINALE = flag


def _emit(riga: str = "") -> None:
    """Punto unico di output: ogni riga passa da qui."""
    _REPORT_LINES.append(riga)
    if _FLAG_STAMPA_TERMINALE:
        print(riga)


def stampa(*args, sep: str = " ") -> None:
    """
    Sostituto di print() da usare al posto dei print "nudi" sparsi nel codice
    (es. in main_manual.py, main_job_auto.py, main_job_single.py), così anche
    quelle righe finiscono nel report.
    """
    _emit(sep.join(str(a) for a in args))


def get_report(separatore: str = "\n") -> str:
    """Restituisce l'intero report accumulato come stringa unica."""
    return separatore.join(_REPORT_LINES)


def get_report_righe() -> list[str]:
    """Restituisce l'intero report come lista di righe (copia)."""
    return list(_REPORT_LINES)


def reset_report() -> None:
    """Svuota il buffer del report. Da chiamare tipicamente a inizio run."""
    global _REPORT_LINES
    _REPORT_LINES = []


def salva_report(path: Path, aggiungi_timestamp_nome: bool = False) -> Path:
    """
    Salva il report accumulato su file locale (crea le cartelle mancanti).
    Se aggiungi_timestamp_nome=True, appende un timestamp al nome del file
    (utile per non sovrascrivere i report delle run precedenti).
    """
    path = Path(path)

    if aggiungi_timestamp_nome:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = path.with_name(f"{path.stem}_{timestamp}{path.suffix}")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(get_report(), encoding="utf-8")
    return path


# ============================================================
# FUNZIONI ORIGINALI — invariate nella firma, usano _emit al posto di print
# ============================================================

def set_indentazione(x: str) -> None:
    global INDENTAZIONE
    INDENTAZIONE = x


def linea() -> None:
    _emit("-" * BLOCK_LENGTH)


def separatore() -> None:
    _emit("=" * BLOCK_LENGTH)


def get_tab(n: int) -> str:
    return INDENTAZIONE * n


def end_all_phases() -> None:
    global _profondita, _flag_riga_vuota
    _profondita = 0
    if not(_flag_riga_vuota):
        _flag_riga_vuota = True
        _emit("")


def new_phase(corpo: str) -> None:
    global _contatore_fase, _profondita, _flag_riga_vuota
    if not(_flag_riga_vuota):
        _flag_riga_vuota = True
        _emit("")
    corpo = corpo.strip()

    if _profondita == 0:
        _contatore_fase += 1
        _emit(f"Fase {_contatore_fase}: {corpo}")
    else:
        _emit(f"{get_tab(_profondita)}{BULLET_PHASE}{corpo}:")

    _profondita += 1


def end_phase() -> None:
    global _profondita, _flag_riga_vuota
    _profondita = max(0, _profondita - 1)
    if not(_flag_riga_vuota):
        _flag_riga_vuota = True
        _emit("")

def riga_libera(testo: str = "") -> None:
    _emit(str(testo))

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
    _emit(f"{get_tab(_profondita)}{BULLET_MEX}[{tipo}]: {corpo}")

    if dettaglio is None:
        return

    if isinstance(dettaglio, str):
        dettaglio = [dettaglio]

    for mex in dettaglio:
        mex = mex.strip()
        if mex:
            _emit(f"{get_tab(_profondita + 2)}{mex}")


def formatta_tabella(df: pd.DataFrame) -> list[str]:
    """
    Converte un DataFrame in righe di una tabella ASCII (con bordi),
    pronte per essere passate come `dettaglio` a tipo_messaggio/ok_mex/warning_mex/ecc.
    Usa la libreria 'tabulate'. Ritorna [] se il DataFrame è vuoto.
    """
    if df.empty:
        return []
    testo = tabulate(df, headers="keys", tablefmt="grid", showindex=False)     #type: ignore
    return testo.split("\n")


def tabella_mex(tipo: str, corpo: str, df: pd.DataFrame) -> None:
    """
    Come tipo_messaggio, ma il dettaglio è un DataFrame stampato come tabella
    ASCII (vedi formatta_tabella). Dopo la tabella viene lasciata una riga vuota.
    """
    global _flag_riga_vuota
    righe = formatta_tabella(df)
    tipo_messaggio(tipo, corpo=corpo, dettaglio=righe if righe else None)
    if righe:
        _flag_riga_vuota = True
        _emit("")


def reset_fase(valore_iniziale: int = 0) -> None:
    global _contatore_fase, _profondita
    _contatore_fase = valore_iniziale
    _profondita = 0
    

# ============================================================
# FUNZIONI MAIL
# ============================================================

import smtplib
from email.message import EmailMessage

def invia_report_mail(report_text: str, destinatario: str):
    msg = EmailMessage()
    msg["Subject"] = "Report flusso Spese-Entrate"
    msg["From"] = "lorenzvittori@gmail.com"
    msg["To"] = destinatario
    msg.set_content(report_text)

    # Gmail richiede SMTP SSL su porta 465
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("lorenzvittori@gmail.com", "cdgn xstu dbgs qzjs")
        smtp.send_message(msg)
