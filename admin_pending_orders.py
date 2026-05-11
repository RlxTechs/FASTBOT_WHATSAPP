import json
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from manual_approval import load_pending, set_decision

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

class PendingOrdersAdmin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FASTBOT — Validation commandes spéciales")
        self.geometry("950x620")
        self.selected_order = None
        self.build()
        self.refresh()

    def build(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        left = ttk.Frame(root)
        left.pack(side="left", fill="y", padx=(0, 10))

        ttk.Label(left, text="Demandes en attente", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.listbox = tk.Listbox(left, width=45, height=28)
        self.listbox.pack(fill="y", expand=True, pady=8)
        self.listbox.bind("<<ListboxSelect>>", self.select_order)

        ttk.Button(left, text="Recharger", command=self.refresh).pack(fill="x", pady=2)

        right = ttk.Frame(root)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(right, text="Détails", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.detail = tk.Text(right, height=16, wrap="word")
        self.detail.pack(fill="both", expand=True, pady=8)

        ttk.Label(right, text="Réponse à envoyer au client").pack(anchor="w")
        self.reply = tk.Text(right, height=8, wrap="word")
        self.reply.pack(fill="x", pady=5)

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=8)

        ttk.Button(btns, text="✅ Disponible maintenant", command=self.approve_now).pack(side="left", padx=3)
        ttk.Button(btns, text="🌙 Possible le soir", command=self.approve_evening).pack(side="left", padx=3)
        ttk.Button(btns, text="❌ Pas disponible", command=self.refuse_now).pack(side="left", padx=3)
        ttk.Button(btns, text="Envoyer réponse personnalisée", command=self.custom_reply).pack(side="right", padx=3)

    def refresh(self):
        self.data = load_pending()
        self.orders = [o for o in self.data.get("orders", []) if o.get("status") == "pending"]

        self.listbox.delete(0, "end")
        for o in self.orders:
            self.listbox.insert(
                "end",
                f"{o.get('created_at')} | {o.get('chat_id')} | {o.get('order_type')} | {o.get('zone')}"
            )

    def select_order(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return

        self.selected_order = self.orders[sel[0]]

        self.detail.delete("1.0", "end")
        self.detail.insert("end", json.dumps(self.selected_order, ensure_ascii=False, indent=2))

        self.reply.delete("1.0", "end")
        self.reply.insert("end", self.default_check_reply())

    def default_check_reply(self):
        return (
            "Merci pour l’attente 🙏\n"
            "Je vérifie la disponibilité et le livreur pour la pizza, puis je vous confirme."
        )

    def ensure_selected(self):
        if not self.selected_order:
            messagebox.showwarning("Attention", "Sélectionne une demande.")
            return False
        return True

    def approve_now(self):
        if not self.ensure_selected():
            return

        msg = (
            "C’est bon ✅ La pizza peut être lancée maintenant.\n\n"
            "Envoyez le modèle choisi + votre numéro + le repère exact, et on confirme le total avec livraison."
        )
        self.reply.delete("1.0", "end")
        self.reply.insert("end", msg)
        self.save_decision("approved_now", msg)

    def approve_evening(self):
        if not self.ensure_selected():
            return

        msg = (
            "Pour maintenant, ce n’est pas sûr à cause du nombre de commandes en cours 🙏\n"
            "Par contre, si vous acceptez pour le soir, là ce sera plus sûr.\n\n"
            "Plusieurs commandes avaient déjà été prévues depuis hier, donc je préfère vous confirmer proprement plutôt que de vous faire attendre inutilement."
        )
        self.reply.delete("1.0", "end")
        self.reply.insert("end", msg)
        self.save_decision("approved_evening", msg)

    def refuse_now(self):
        if not self.ensure_selected():
            return

        msg = (
            "Désolé 🙏 Pour la pizza, ce ne sera pas possible maintenant.\n"
            "On a beaucoup de commandes en cours et je préfère être honnête pour éviter de vous faire attendre inutilement.\n\n"
            "Vous pouvez choisir un autre plat disponible si vous voulez."
        )
        self.reply.delete("1.0", "end")
        self.reply.insert("end", msg)
        self.save_decision("refused_now", msg)

    def custom_reply(self):
        if not self.ensure_selected():
            return

        msg = self.reply.get("1.0", "end").strip()
        if not msg:
            messagebox.showwarning("Attention", "La réponse est vide.")
            return

        self.save_decision("custom", msg)

    def save_decision(self, decision, msg):
        ok = set_decision(self.selected_order["id"], decision, msg)
        if ok:
            messagebox.showinfo("OK", "Décision enregistrée. Le bot l’enverra quand il repassera dans cette conversation.")
            self.refresh()
        else:
            messagebox.showerror("Erreur", "Impossible d’enregistrer la décision.")

if __name__ == "__main__":
    app = PendingOrdersAdmin()
    app.mainloop()
