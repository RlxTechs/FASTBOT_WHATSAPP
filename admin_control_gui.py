import json
import time
import subprocess
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
    "autonomous_mode_enabled": True,
    "auto_scan_unread_chats": True,
    "patrol_use_unread_filter": True,
    "patrol_coordinate_fallback": True,
    "patrol_changed_chats": True,
    "patrol_new_rows": True,
    "skip_if_message_box_not_empty": False,
    "audit_all_visible_messages": True,
    "auto_send_only_safe": True,
    "block_on_unknown_campaign": False,
    "auto_followup_enabled": False,
    "pause_when_user_active": True,
    "confidence_required": 0.88,
    "auto_send_delay_seconds": 0.8,
    "patrol_min_seconds_between_same_chat": 8,
    "patrol_coordinate_cycle_seconds": 3,
    "patrol_recent_limit": 8,
    "followup_after_minutes_1": 20,
    "followup_after_minutes_2": 60
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

class ScrollableFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = ttk.Frame(self.canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.window = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self.resize_inner)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def resize_inner(self, event):
        self.canvas.itemconfig(self.window, width=event.width)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FASTBOT V11 — Admin Autonomie WhatsApp")
        self.minsize(900, 650)
        self.geometry("1050x760")
        self.resizable(True, True)

        self.data = load_settings()
        self.vars = {}
        self.entries = {}

        self.build()

        # Ouvre en maximisé sur Windows
        self.after(200, self.maximize_window)

    def maximize_window(self):
        try:
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                pass

    def add_bool(self, parent, key, label, desc):
        f = ttk.Frame(parent)
        f.pack(fill="x", pady=5)

        v = tk.BooleanVar(value=bool(self.data.get(key, DEFAULTS.get(key, False))))
        self.vars[key] = v

        ttk.Checkbutton(f, text=label, variable=v).pack(anchor="w")
        ttk.Label(f, text=desc, foreground="#555").pack(anchor="w", padx=25)

    def add_buttons(self, parent):
        btns = ttk.Frame(parent)
        btns.pack(fill="x", pady=8)

        ttk.Button(btns, text="💾 Sauvegarder", command=self.save).pack(side="left", padx=4)
        ttk.Button(btns, text="✅ Tester sauvegarde", command=self.test_save).pack(side="left", padx=4)
        ttk.Button(btns, text="🛡️ Mode prudent", command=self.safe_mode).pack(side="left", padx=4)
        ttk.Button(btns, text="🤖 Mode autonome", command=self.auto_mode).pack(side="left", padx=4)
        ttk.Button(btns, text="🎯 Calibrer coordonnées", command=self.calibrate).pack(side="left", padx=4)
        ttk.Button(btns, text="🪟 Plein écran", command=self.maximize_window).pack(side="left", padx=4)

    def build(self):
        main = ttk.Frame(self, padding=10)
        main.pack(fill="both", expand=True)

        # Barre du haut toujours visible
        top = ttk.Frame(main)
        top.pack(fill="x")

        ttk.Label(
            top,
            text="FASTBOT V11 — Admin Autonomie WhatsApp",
            font=("Segoe UI", 16, "bold")
        ).pack(anchor="w")

        self.status = ttk.Label(top, text="Réglages chargés.", foreground="green")
        self.status.pack(anchor="w", pady=(3, 6))

        self.add_buttons(top)

        ttk.Separator(main).pack(fill="x", pady=6)

        # Zone scrollable
        scroll = ScrollableFrame(main)
        scroll.pack(fill="both", expand=True)

        root = scroll.inner

        powers = ttk.LabelFrame(root, text="Autonomie du bot", padding=10)
        powers.pack(fill="x", pady=6, padx=4)

        self.add_bool(powers, "send_automatically", "Envoyer automatiquement", "Le bot appuie sur Entrée après avoir écrit.")
        self.add_bool(powers, "autonomous_mode_enabled", "Mode autonome", "Le bot patrouille tout seul dans WhatsApp.")
        self.add_bool(powers, "auto_scan_unread_chats", "Scanner les Non lues", "Le bot clique sur l’onglet Non lues.")
        self.add_bool(powers, "patrol_use_unread_filter", "Utiliser le bouton Non lues", "Important pour ton WhatsApp Web.")
        self.add_bool(powers, "patrol_coordinate_fallback", "Fallback coordonnées écran", "Si Selenium ne voit rien, le bot clique avec les coordonnées calibrées.")
        self.add_bool(powers, "patrol_changed_chats", "Détecter aperçu changé", "Utile si le badge non lu n’est pas détecté.")
        self.add_bool(powers, "patrol_new_rows", "Traiter nouvelles lignes", "Utile pour les nouveaux clients qui remontent en haut.")

        safety = ttk.LabelFrame(root, text="Sécurité / comportement", padding=10)
        safety.pack(fill="x", pady=6, padx=4)

        self.add_bool(safety, "skip_if_message_box_not_empty", "Ne pas écraser brouillon", "OFF recommandé en autonomie. ON si tu écris souvent toi-même.")
        self.add_bool(safety, "audit_all_visible_messages", "Logs complets", "Affiche/journalise messages clients, bot, manuels, supprimés.")
        self.add_bool(safety, "auto_send_only_safe", "Envoyer seulement si safe", "Le bot envoie seulement si la réponse est sûre.")
        self.add_bool(safety, "block_on_unknown_campaign", "Bloquer pub inconnue", "OFF recommandé pour continuer si le message client est clair.")
        self.add_bool(safety, "auto_followup_enabled", "Relances automatiques", "À activer seulement quand le bot est stable.")
        self.add_bool(safety, "pause_when_user_active", "Pause quand je touche souris/clavier", "Le bot attend ton inactivité avant de reprendre.")

        nums = ttk.LabelFrame(root, text="Valeurs techniques", padding=10)
        nums.pack(fill="x", pady=6, padx=4)

        fields = [
            ("confidence_required", "Confiance minimum"),
            ("auto_send_delay_seconds", "Délai avant envoi"),
            ("patrol_min_seconds_between_same_chat", "Cooldown même chat"),
            ("patrol_coordinate_cycle_seconds", "Cycle coordonnées"),
            ("patrol_recent_limit", "Nombre lignes récentes"),
            ("followup_after_minutes_1", "Relance 1 après minutes"),
            ("followup_after_minutes_2", "Relance 2 après minutes"),
            ("resume_after_user_idle_seconds", "Reprise après inactivité sec"),
            ("poll_seconds", "Vitesse boucle sec")
        ]

        for i, (key, label) in enumerate(fields):
            ttk.Label(nums, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=5)

            var = tk.StringVar(value=str(self.data.get(key, DEFAULTS.get(key))))
            self.entries[key] = var

            ttk.Entry(nums, textvariable=var, width=14).grid(row=i, column=1, sticky="w", padx=5, pady=5)

        info = ttk.LabelFrame(root, text="Fichiers utiles", padding=10)
        info.pack(fill="x", pady=6, padx=4)

        ttk.Label(info, text="settings.json : réglages sauvegardés").pack(anchor="w")
        ttk.Label(info, text="ui_coordinates.json : coordonnées de clic calibrées").pack(anchor="w")
        ttk.Label(info, text="patrol_debug.jsonl : pourquoi le bot clique ou ne clique pas").pack(anchor="w")
        ttk.Label(info, text="audit_messages.jsonl : messages visibles WhatsApp").pack(anchor="w")
        ttk.Label(info, text="bot_decisions.jsonl : décisions du bot").pack(anchor="w")

        # Boutons en bas aussi, accessibles avec scroll
        bottom = ttk.LabelFrame(root, text="Actions", padding=10)
        bottom.pack(fill="x", pady=10, padx=4)

        self.add_buttons(bottom)

    def collect(self):
        for k, v in self.vars.items():
            self.data[k] = bool(v.get())

        for k, var in self.entries.items():
            raw = var.get().replace(",", ".")
            try:
                if k in {"patrol_recent_limit"}:
                    self.data[k] = int(float(raw))
                else:
                    self.data[k] = float(raw)
            except Exception:
                self.data[k] = DEFAULTS.get(k)

    def save(self):
        self.collect()
        save_settings(self.data)
        self.status.config(text="✅ Sauvegardé dans settings.json à " + time.strftime("%H:%M:%S"), foreground="green")
        messagebox.showinfo("OK", "Réglages sauvegardés dans settings.json.")

    def test_save(self):
        self.collect()
        save_settings(self.data)
        reread = load_settings()

        ok = True
        for k, v in self.data.items():
            if reread.get(k) != v:
                ok = False
                break

        if ok:
            self.status.config(text="✅ Test sauvegarde OK.", foreground="green")
            messagebox.showinfo("OK", "La sauvegarde fonctionne.")
        else:
            self.status.config(text="❌ Test sauvegarde échoué.", foreground="red")
            messagebox.showerror("Erreur", "settings.json n’a pas été relu correctement.")

    def safe_mode(self):
        self.vars["send_automatically"].set(False)
        self.vars["autonomous_mode_enabled"].set(False)
        self.vars["auto_scan_unread_chats"].set(False)
        self.vars["auto_followup_enabled"].set(False)
        self.save()

    def auto_mode(self):
        self.vars["send_automatically"].set(True)
        self.vars["autonomous_mode_enabled"].set(True)
        self.vars["auto_scan_unread_chats"].set(True)
        self.vars["patrol_use_unread_filter"].set(True)
        self.vars["patrol_coordinate_fallback"].set(True)
        self.vars["patrol_changed_chats"].set(True)
        self.vars["patrol_new_rows"].set(True)
        self.vars["skip_if_message_box_not_empty"].set(False)
        self.vars["audit_all_visible_messages"].set(True)
        self.vars["auto_send_only_safe"].set(True)
        self.save()

    def calibrate(self):
        bat = BASE_DIR / "calibrate_ui.bat"
        if not bat.exists():
            messagebox.showerror("Erreur", "calibrate_ui.bat introuvable.")
            return
        subprocess.Popen(["cmd", "/c", str(bat)], cwd=str(BASE_DIR))

if __name__ == "__main__":
    App().mainloop()
