import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

SETTINGS = BASE_DIR / "settings.json"

DEFAULTS = {
    "send_automatically": False,
    "autonomous_mode_enabled": False,
    "auto_scan_unread_chats": False,
    "auto_scan_when_idle_seconds": 4,
    "learn_from_my_messages": True,
    "audit_all_visible_messages": True,
    "pause_on_deleted_message": True,
    "skip_conversation_ouverte": True,
    "confidence_required": 0.88,
    "auto_send_only_safe": True,
    "precheck_verbose": False,
    "precheck_rescan_known_after_seconds": 3600,
    "precheck_rescan_after_seconds": 180
}

def load_settings():
    try:
        data = json.loads(SETTINGS.read_text(encoding="utf-8-sig")) if SETTINGS.exists() else {}
    except Exception:
        data = {}

    for k, v in DEFAULTS.items():
        data.setdefault(k, v)

    return data

def save_settings(data):
    SETTINGS.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class AdminControl(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FASTBOT WhatsApp — Contrôle PRO")
        self.geometry("700x610")
        self.resizable(False, False)
        self.data = load_settings()
        self.vars = {}
        self.build()

    def add_bool(self, parent, key, label, desc):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=6)
        var = tk.BooleanVar(value=bool(self.data.get(key, False)))
        self.vars[key] = var
        ttk.Checkbutton(frame, text=label, variable=var).pack(anchor="w")
        ttk.Label(frame, text=desc, foreground="#555").pack(anchor="w", padx=24)

    def build(self):
        root = ttk.Frame(self, padding=15)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="FASTBOT — Mode autonome & logs", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(root, text="Ces réglages permettent de revendre/configurer le bot sans toucher au code.").pack(anchor="w", pady=(0,12))

        self.add_bool(root, "send_automatically", "Envoyer automatiquement", "Si OFF : le bot colle la réponse mais ne l’envoie pas.")
        self.add_bool(root, "autonomous_mode_enabled", "Mode 100% autonome", "Le bot peut aller dans les conversations non lues.")
        self.add_bool(root, "auto_scan_unread_chats", "Scanner les conversations non lues", "Le bot cherche les nouveaux messages dans la liste WhatsApp.")
        self.add_bool(root, "audit_all_visible_messages", "Journaliser tous les messages visibles", "Entrants, sortants, manuels, auto, supprimés.")
        self.add_bool(root, "learn_from_my_messages", "Apprendre de mes corrections", "Enregistre tes suppressions et messages manuels dans human_corrections.jsonl.")
        self.add_bool(root, "pause_on_deleted_message", "Se calmer après message supprimé", "Évite de répondre encore après une suppression.")
        self.add_bool(root, "auto_send_only_safe", "Envoyer seulement les réponses sûres", "Sécurité pour éviter les mauvaises réponses.")
        self.add_bool(root, "precheck_verbose", "Afficher tous les prechecks", "À désactiver si les logs deviennent trop bavards.")

        row = ttk.Frame(root)
        row.pack(fill="x", pady=10)
        ttk.Label(row, text="Confiance minimum auto-send :").pack(side="left")
        self.conf_var = tk.StringVar(value=str(self.data.get("confidence_required", 0.88)))
        ttk.Entry(row, textvariable=self.conf_var, width=8).pack(side="left", padx=8)

        row2 = ttk.Frame(root)
        row2.pack(fill="x", pady=8)
        ttk.Label(row2, text="Délai scan auto, secondes :").pack(side="left")
        self.delay_var = tk.StringVar(value=str(self.data.get("auto_scan_when_idle_seconds", 4)))
        ttk.Entry(row2, textvariable=self.delay_var, width=8).pack(side="left", padx=8)

        btns = ttk.Frame(root)
        btns.pack(fill="x", pady=18)

        ttk.Button(btns, text="Sauvegarder", command=self.save).pack(side="left", padx=4)
        ttk.Button(btns, text="Mode prudent", command=self.safe_mode).pack(side="left", padx=4)
        ttk.Button(btns, text="Mode autonome", command=self.autonomous_mode).pack(side="left", padx=4)
        ttk.Button(btns, text="Quitter", command=self.destroy).pack(side="right", padx=4)

        ttk.Label(root, text="Logs importants :", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(15, 2))
        ttk.Label(root, text="audit_messages.jsonl = tous les messages visibles").pack(anchor="w")
        ttk.Label(root, text="bot_decisions.jsonl = décisions du bot").pack(anchor="w")
        ttk.Label(root, text="human_corrections.jsonl = suppressions / corrections humaines").pack(anchor="w")

    def save(self):
        for k, v in self.vars.items():
            self.data[k] = bool(v.get())

        try:
            self.data["confidence_required"] = float(self.conf_var.get().replace(",", "."))
        except Exception:
            self.data["confidence_required"] = 0.88

        try:
            self.data["auto_scan_when_idle_seconds"] = float(self.delay_var.get().replace(",", "."))
        except Exception:
            self.data["auto_scan_when_idle_seconds"] = 4

        self.data["precheck_rescan_known_after_seconds"] = 3600
        self.data["precheck_rescan_after_seconds"] = 180

        save_settings(self.data)
        messagebox.showinfo("OK", "Réglages sauvegardés.")

    def safe_mode(self):
        self.vars["send_automatically"].set(False)
        self.vars["autonomous_mode_enabled"].set(False)
        self.vars["auto_scan_unread_chats"].set(False)
        self.save()

    def autonomous_mode(self):
        self.vars["send_automatically"].set(True)
        self.vars["autonomous_mode_enabled"].set(True)
        self.vars["auto_scan_unread_chats"].set(True)
        self.vars["auto_send_only_safe"].set(True)
        self.vars["audit_all_visible_messages"].set(True)
        self.save()

if __name__ == "__main__":
    app = AdminControl()
    app.mainloop()
