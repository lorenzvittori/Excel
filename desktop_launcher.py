# desktop_launcher.py
import subprocess
import sys
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog


def get_project_dir():
    """Restituisce la cartella dove risiede questo script."""
    return os.path.dirname(os.path.abspath(__file__))


def run_flow():
    """Esegue main_job_auto.py catturando tutto l'output."""
    script_dir = get_project_dir()
    main_script = os.path.join(script_dir, "main_job_auto.py")

    result = subprocess.run(
        [sys.executable, main_script],
        cwd=script_dir,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result


class ReportWindow:
    """Finestra che mostra il report finale."""

    def __init__(self, result: subprocess.CompletedProcess):
        self.result = result
        self.root = tk.Tk()
        self.root.title("Report Flusso Spese-Entrate")
        self.root.geometry("1000x750")

        # --- Barra di stato ---
        success = result.returncode == 0
        status_text = "✅ FLUSSO COMPLETATO CON SUCCESSO" if success else "❌ FLUSSO TERMINATO CON ERRORI"
        status_color = "green" if success else "red"

        tk.Label(
            self.root,
            text=status_text,
            fg=status_color,
            font=("Segoe UI", 14, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))

        # --- Area testo scrollabile ---
        self.txt = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, font=("Consolas", 10)
        )
        self.txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        full_output = result.stdout
        if result.stderr:
            full_output += "\n\n=== STDERR ===\n" + result.stderr

        self.txt.insert(tk.END, full_output)
        self.txt.config(state=tk.DISABLED)
        self.full_text = full_output

        # --- Pulsanti ---
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="📋 Copia Report", command=self.copy).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="💾 Salva su file", command=self.save).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(btn_frame, text="❌ Chiudi", command=self.root.destroy).pack(
            side=tk.RIGHT, padx=5
        )

    def copy(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.full_text)
        messagebox.showinfo("Copiato", "Report copiato negli appunti!")

    def save(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("File di testo", "*.txt"), ("Tutti i file", "*.*")],
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.full_text)
            messagebox.showinfo("Salvato", f"Report salvato in:\n{path}")

    def show(self):
        self.root.mainloop()


class LoadingWindow:
    """Finestra di attesa che gira il flusso in un thread separato."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Elaborazione in corso...")
        self.root.geometry("400x150")
        self.root.resizable(False, False)

        tk.Label(
            self.root,
            text="⏳ Sto eseguendo il flusso automatico...",
            font=("Segoe UI", 12),
        ).pack(pady=20)
        tk.Label(
            self.root,
            text="Attendere il completamento...",
            font=("Segoe UI", 10),
            fg="gray",
        ).pack()

        self.result = None

    def start_flow(self):
        def task():
            self.result = run_flow()
            # Torna nel thread principale per chiudere questa finestra
            self.root.after(0, self.finish)

        threading.Thread(target=task, daemon=True).start()
        self.root.mainloop()

    def finish(self):
        self.root.destroy()
        ReportWindow(self.result).show()    #type: ignore


if __name__ == "__main__":
    LoadingWindow().start_flow()