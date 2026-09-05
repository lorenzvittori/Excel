#NOME MODULO: logger.py
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
from tabulate import tabulate

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

def ok_mex(corpo: str, tabella: pd.DataFrame | None = None, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("OK", corpo=corpo, tabella=tabella, dettaglio=dettaglio)


def info_mex(corpo: str, tabella: pd.DataFrame | None = None, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("INFO", corpo=corpo, tabella=tabella, dettaglio=dettaglio)


def error_mex(corpo: str, tabella: pd.DataFrame | None = None, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("ERROR", corpo=corpo, tabella=tabella, dettaglio=dettaglio)


def warning_mex(corpo: str, tabella: pd.DataFrame | None = None, dettaglio: str | list[str] | None = None) -> None:
    tipo_messaggio("WARNING", corpo=corpo, tabella=tabella, dettaglio=dettaglio)


def _righe_tabella_ascii(tabella: pd.DataFrame) -> list[str]:
    """Renderizza un DataFrame come tabella ASCII (bordi in caratteri +/-/|),
    leggibile sia a terminale sia dentro la mail di riepilogo in testo semplice."""
    testo = tabulate(
        tabella.fillna(""),
        headers="keys",
        tablefmt="grid",
        showindex=False,
    )
    return testo.split("\n")


def tipo_messaggio(
        tipo: str,
        corpo: str,
        tabella: pd.DataFrame | None = None,
        dettaglio: str | list[str] | None = None) -> None:
    global _flag_riga_vuota
    _flag_riga_vuota = False
    tipo = tipo.strip()
    corpo = corpo.strip()
    _emit(f"{get_tab(_profondita)}{BULLET_MEX}[{tipo}]: {corpo}")

    if tabella is not None and not tabella.empty:
        for riga in _righe_tabella_ascii(tabella):
            _emit(f"{get_tab(_profondita + 2)}{riga}")

    if dettaglio is None:
        return

    if isinstance(dettaglio, str):
        dettaglio = [dettaglio]

    for mex in dettaglio:
        mex = mex.strip()
        if mex:
            _emit(f"{get_tab(_profondita + 2)}{mex}")


def reset_fase(valore_iniziale: int = 0) -> None:
    global _contatore_fase, _profondita
    _contatore_fase = valore_iniziale
    _profondita = 0
    

# ============================================================
# FUNZIONI MAIL
# ============================================================

import os
import smtplib
from email.message import EmailMessage

def invia_report_mail(report_text: str, destinatario: str):
    mittente = "lorenzvittori@gmail.com"

    password = os.environ.get("GMAIL_APP_PASSWORD")
    if not password:
        error_mex(
            "Variabile d'ambiente GMAIL_APP_PASSWORD mancante: impossibile inviare la mail"
        )
        raise ValueError("GMAIL_APP_PASSWORD non impostata")

    msg = EmailMessage()
    msg["Subject"] = "Report flusso Spese-Entrate"
    msg["From"] = mittente
    msg["To"] = destinatario
    msg.set_content(report_text)

    # Gmail richiede SMTP SSL su porta 465
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(mittente, password)
        smtp.send_message(msg)
