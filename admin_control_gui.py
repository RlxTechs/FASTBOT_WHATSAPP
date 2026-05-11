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
    "send_automatically": True,
    "autonomous_mode_enabled": False,
    "auto_scan_unread_chats": False,
    "patrol_recent_chats": False,
    "patrol_recent_limit": 8,
    "auto_followup_enabled": False,
    "followup_after_minutes_1": 20,
    "followup_after_minutes_2": 60,
    "audit_all_visible_messages": True,
    "confidence_required": 0.88,
    "auto_send_only_safe": True,
    "auto_send_delay_seconds": 0.8,
    "skip_if_message_box_not_empty": True,
    "precheck_verbose": False,
    "block_on_unknown_campaign": False
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

class AdminV8(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FASTBOT V8.1 — Contrôle autonomie")
        self.geometry("760x680")
        self.resizable(False, False)
        self.data = load_settings()
        self.vars = {}
        self.build()

    def add_bool(self, parent, key, label, desc):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", pady=5)
        var = tk.BooleanVar(value=bool(self.data.get(key, False)))
        self.vars[key] = var
        ttk.Checkbutton(frame, text=label, variable=var).pack(anchor="w")
        ttk.Label(frame, text=desc, foreground="#555").pack(anchor="w", padx=24)

    def build(self):
        root = ttk.Frame(self, padding=15)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="FASTBOT V8.1 — Autonomie commerciale", font=("Segoe UI", 16, "bold")).pack(anchor="w")
        ttk.Label(root, text="Active/désactive les pouvoirs du bot sans toucher au code.").pack(anchor="w", pady=(0, 12))

        self.add_bool(root, "send_automatically", "Envoyer automatiquement", "Si OFF : le bot colle seulement la réponse.")
        self.add_bool(root, "autonomous_mode_enabled", "Mode 100% autonome", "Autorise le bot à patrouiller lui-même.")
        self.add_bool(root, "auto_scan_unread_chats", "Scanner conversations non lues", "Le bot ouvre les nouveaux messages.")
        self.add_bool(root, "patrol_recent_chats", "Patrouiller conversations récentes", "À utiliser prudemment : il visite aussi les discussions récentes.")
        self.add_bool(root, "auto_followup_enabled", "Relances automatiques", "Le bot relance doucement si le client ne répond pas.")
        self.add_bool(root, "audit_all_visible_messages", "Journaliser tous les messages visibles", "Entrants, sortants, manuels, auto, supprimés.")
        self.add_bool(root, "auto_send_only_safe", "Envoyer seulement réponses sûres", "Évite l’envoi si le score/contexte n’est pas fiable.")
        self.add_bool(root, "skip_if_message_box_not_empty", "Ne pas écraser un brouillon", "Sécurité si tu as déjà écrit quelque chose.")
        self.add_bool(root, "block_on_unknown_campaign", "Bloquer si pub inconnue", "OFF recommandé : le bot continue si le message client est clair.")

        row = ttk.Frame(root)
        row.pack(fill="x", pady=12)

        ttk.Label(row, text="Confiance minimum :").pack(side="left")
        self.conf_var = tk.StringVar(value=str(self.data.get("confidence_required", 0.88)))
        ttk.Entry(row, textvariable=self.conf_var, width=8).pack(side="left", padx=8)

        ttk.Label(row, text="Délai envoi :").pack(side="left", padx=(20, 0))
        self.delay_var = tk.StringVar(value=str(self.data.get("auto_send_delay_seconds", 0.8)))
        ttk.Entry(row, textvariable=self.delay_var, width=8).pack(side="left", padx=8)

        row2 = ttk.Frame(root)
        row2.pack(fill="x", pady=8)

        ttk.Label(row2, text="Relance 1 après min :").pack(side="left")
        self.f1_var = tk.StringVar(value=str(self.data.get("followup_after_minutes_1", 20)))
        ttk.Entry(row2, textvariable=self.f1_var, width=8).pack(side="left", padx=8)

        ttk.Label(row2, text="Relance 2 après min :").pack(side="left", padx=(20, 0))
        self.f2_var = tk.StringVar(value=str(self.data.get("followup_after_minutes_2", 60)))
        ttk.Entry(row2, textvariable=self.f2_var, width=8).pack(side="left", padx=8)

        row3 = ttk.Frame(root)
        row3.pack(fill="x", pady=8)

        ttk.Label(row3, text="Limite conversations récentes :").pack(side="left")
        self.recent_var = tk.StringVar(value=str(self.data.get("patrol_recent_limit", 8)))
        ttk.Entry(row3, textvariable=self.recent_var, width=8).pack(side="left", padx=8)

        btns = ttk.Frame(root)
        btns.pack(fill="x", pady=20)

        ttk.Button(btns, text="Sauvegarder", command=self.save).pack(side="left", padx=4)
        ttk.Button(btns, text="Mode prudent", command=self.safe_mode).pack(side="left", padx=4)
        ttk.Button(btns, text="Mode autonome", command=self.auto_mode).pack(side="left", padx=4)
        ttk.Button(btns, text="Quitter", command=self.destroy).pack(side="right", padx=4)

        ttk.Label(root, text="Fichiers utiles :", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(10, 2))
        ttk.Label(root, text="lead_memory.json = mémoire client / étape de vente").pack(anchor="w")
        ttk.Label(root, text="audit_messages.jsonl = tout ce que WhatsApp affiche").pack(anchor="w")
        ttk.Label(root, text="bot_decisions.jsonl = pourquoi le bot a répondu").pack(anchor="w")

    def save(self):
        for k, v in self.vars.items():
            self.data[k] = bool(v.get())

        def f(var, default):
            try:
                return float(var.get().replace(",", "."))
            except Exception:
                return default

        def i(var, default):
            try:
                return int(float(var.get().replace(",", ".")))
            except Exception:
                return default

        self.data["confidence_required"] = f(self.conf_var, 0.88)
        self.data["auto_send_delay_seconds"] = f(self.delay_var, 0.8)
        self.data["followup_after_minutes_1"] = f(self.f1_var, 20)
        self.data["followup_after_minutes_2"] = f(self.f2_var, 60)
        self.data["patrol_recent_limit"] = i(self.recent_var, 8)

        save_settings(self.data)
        messagebox.showinfo("OK", "Réglages sauvegardés.")

    def safe_mode(self):
        self.vars["send_automatically"].set(False)
        self.vars["autonomous_mode_enabled"].set(False)
        self.vars["auto_scan_unread_chats"].set(False)
        self.vars["patrol_recent_chats"].set(False)
        self.vars["auto_followup_enabled"].set(False)
        self.save()

    def auto_mode(self):
        self.vars["send_automatically"].set(True)
        self.vars["autonomous_mode_enabled"].set(True)
        self.vars["auto_scan_unread_chats"].set(True)
        self.vars["audit_all_visible_messages"].set(True)
        self.vars["auto_send_only_safe"].set(True)
        self.save()

if __name__ == "__main__":
    app = AdminV8()
    app.mainloop()
