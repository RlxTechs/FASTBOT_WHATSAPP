import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from pathlib import Path
from PIL import Image, ImageTk

BASE = Path(__file__).resolve().parent
UNKNOWN = BASE / "unknown_campaigns.json"
CAMPAIGNS = BASE / "campaigns.json"
STATE = BASE / "conversations_state.json"
SALES = BASE / "sales_config.json"

def load(path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        pass
    return default

def save(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def campaign_patch(c):
    patch = {
        "needs_campaign_label": False,
        "campaign_id": c.get("id", ""),
        "campaign_label": c.get("label", ""),
        "campaign_category": c.get("category", ""),
        "campaign_intent": c.get("intent", ""),
        "campaign_product_id": c.get("product_id", ""),
        "campaign_product_query": c.get("product_query", ""),
        "last_category": c.get("category", "")
    }
    if c.get("product_id"):
        patch["last_product_id"] = c.get("product_id")
    return patch

def update_state(card_hash, camp, chat_example):
    state = load(STATE, {})
    patch = campaign_patch(camp)
    changed = 0

    for chat_id, st in list(state.items()):
        if st.get("unknown_campaign_hash") == card_hash or chat_id == chat_example:
            st.update(patch)
            st.pop("unknown_campaign_hash", None)
            st.pop("unknown_campaign_source", None)
            st.pop("unknown_campaign_image", None)
            state[chat_id] = st
            changed += 1

    save(STATE, state)
    return changed

class Admin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCG Bot — Admin Sales")
        self.geometry("1150x720")
        self.minsize(1000, 650)

        self.unknown_data = {}
        self.campaigns_data = {}
        self.sales_data = {}
        self.waiting = []
        self.selected_unknown = None
        self.current_img = None

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)

        self.build_unknown_tab()
        self.build_food_tab()
        self.build_catalog_tab()
        self.build_campaign_tab()

        self.reload_all()

    def build_unknown_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Miniatures inconnues")

        left = ttk.Frame(tab)
        left.pack(side="left", fill="y", padx=(0,10))

        ttk.Label(left, text="Cartes Facebook inconnues", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.unknown_list = tk.Listbox(left, width=42, height=28)
        self.unknown_list.pack(fill="y", expand=True, pady=8)
        self.unknown_list.bind("<<ListboxSelect>>", self.select_unknown)

        ttk.Button(left, text="Recharger", command=self.reload_all).pack(fill="x", pady=2)
        ttk.Button(left, text="Marquer comme MENU nourriture", command=self.mark_menu).pack(fill="x", pady=2)

        center = ttk.Frame(tab)
        center.pack(side="left", fill="both", expand=True)

        ttk.Label(center, text="Aperçu miniature", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.img_label = ttk.Label(center, text="Sélectionne une miniature", anchor="center")
        self.img_label.pack(fill="both", expand=True)

        self.card_text = tk.Text(center, height=8, wrap="word")
        self.card_text.pack(fill="x", pady=5)

        right = ttk.Frame(tab)
        right.pack(side="right", fill="y", padx=(10,0))

        ttk.Label(right, text="Attribuer campagne", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.campaign_var = tk.StringVar()
        self.campaign_combo = ttk.Combobox(right, textvariable=self.campaign_var, width=42, state="readonly")
        self.campaign_combo.pack(fill="x", pady=8)

        ttk.Button(right, text="Attribuer", command=self.assign_unknown).pack(fill="x", pady=3)
        ttk.Button(right, text="Créer campagne", command=self.create_campaign_popup).pack(fill="x", pady=3)

    def build_food_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Menu nourriture")

        ttk.Label(tab, text="Menu nourriture — une ligne par plat : Nom | Prix", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.food_text = tk.Text(tab, wrap="word")
        self.food_text.pack(fill="both", expand=True, pady=8)

        ttk.Button(tab, text="Sauvegarder menu", command=self.save_food_menu).pack(anchor="e")

    def build_catalog_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Réponse catalogue")

        ttk.Label(tab, text="Réponse globale quand le client dit : vous avez quoi / montrez ce que vous faites", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        self.catalog_text = tk.Text(tab, wrap="word")
        self.catalog_text.pack(fill="both", expand=True, pady=8)

        ttk.Button(tab, text="Sauvegarder réponse catalogue", command=self.save_catalog).pack(anchor="e")

    def build_campaign_tab(self):
        tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(tab, text="Campagnes")

        left = ttk.Frame(tab)
        left.pack(side="left", fill="y", padx=(0,10))

        self.campaign_list = tk.Listbox(left, width=42, height=30)
        self.campaign_list.pack(fill="y", expand=True)
        self.campaign_list.bind("<<ListboxSelect>>", self.select_campaign_json)

        ttk.Button(left, text="Nouvelle campagne vide", command=self.new_campaign_json).pack(fill="x", pady=4)
        ttk.Button(left, text="Recharger", command=self.reload_all).pack(fill="x", pady=2)

        right = ttk.Frame(tab)
        right.pack(side="left", fill="both", expand=True)

        ttk.Label(right, text="Modifier campagne en JSON", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.campaign_json_text = tk.Text(right, wrap="none")
        self.campaign_json_text.pack(fill="both", expand=True, pady=8)

        ttk.Button(right, text="Sauvegarder campagne JSON", command=self.save_campaign_json).pack(anchor="e")

    def reload_all(self):
        self.unknown_data = load(UNKNOWN, {"unknown": {}})
        self.campaigns_data = load(CAMPAIGNS, {"campaigns": []})
        self.sales_data = load(SALES, {"food": {"items": []}, "non_food": {}})

        self.waiting = [r for r in self.unknown_data.get("unknown", {}).values() if r.get("label_status") == "waiting_label"]

        self.unknown_list.delete(0, "end")
        for r in self.waiting:
            self.unknown_list.insert("end", f"{r.get('hash')} | {r.get('chat_example','')}")

        combo_values = [f"{c.get('id')} — {c.get('label')}" for c in self.campaigns_data.get("campaigns", [])]
        self.campaign_combo["values"] = combo_values
        if combo_values:
            self.campaign_combo.current(0)

        self.campaign_list.delete(0, "end")
        for c in self.campaigns_data.get("campaigns", []):
            self.campaign_list.insert("end", f"{c.get('id')} — {c.get('label')}")

        self.load_food_text()
        self.load_catalog_text()

    def load_food_text(self):
        self.food_text.delete("1.0", "end")
        for item in self.sales_data.get("food", {}).get("items", []):
            self.food_text.insert("end", f"{item.get('name')} | {item.get('price')}\n")

    def load_catalog_text(self):
        self.catalog_text.delete("1.0", "end")
        self.catalog_text.insert("end", self.sales_data.get("non_food", {}).get("catalog_overview", ""))

    def select_unknown(self, event=None):
        sel = self.unknown_list.curselection()
        if not sel:
            return
        self.selected_unknown = self.waiting[sel[0]]

        self.card_text.delete("1.0", "end")
        self.card_text.insert("end", json.dumps(self.selected_unknown, ensure_ascii=False, indent=2))

        img_path = self.selected_unknown.get("image", "")
        if img_path and Path(img_path).exists():
            img = Image.open(img_path)
            img.thumbnail((560, 430))
            self.current_img = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self.current_img, text="")
        else:
            self.img_label.configure(text="Pas d’image disponible", image="")

    def selected_campaign(self):
        val = self.campaign_var.get()
        if not val:
            return None
        cid = val.split(" — ")[0].strip()
        for c in self.campaigns_data.get("campaigns", []):
            if c.get("id") == cid:
                return c
        return None

    def assign_unknown(self):
        if not self.selected_unknown:
            messagebox.showwarning("Attention", "Sélectionne une miniature.")
            return
        camp = self.selected_campaign()
        if not camp:
            messagebox.showwarning("Attention", "Sélectionne une campagne.")
            return

        h = self.selected_unknown.get("hash")
        chat = self.selected_unknown.get("chat_example", "")

        camp.setdefault("hashes", [])
        if h not in camp["hashes"]:
            camp["hashes"].append(h)

        self.unknown_data["unknown"][h]["label_status"] = "labeled"
        self.unknown_data["unknown"][h]["campaign_id"] = camp.get("id")
        self.unknown_data["unknown"][h]["campaign_label"] = camp.get("label")

        save(CAMPAIGNS, self.campaigns_data)
        save(UNKNOWN, self.unknown_data)

        changed = update_state(h, camp, chat)
        messagebox.showinfo("OK", f"Attribué à {camp.get('label')}\nConversations mises à jour : {changed}")
        self.reload_all()

    def mark_menu(self):
        for c in self.campaigns_data.get("campaigns", []):
            if c.get("id") == "menu_food":
                self.campaign_var.set(f"{c.get('id')} — {c.get('label')}")
                self.assign_unknown()
                return
        messagebox.showerror("Erreur", "Campagne menu_food introuvable.")

    def create_campaign_popup(self):
        cid = simpledialog.askstring("Campagne", "ID court")
        if not cid:
            return
        label = simpledialog.askstring("Campagne", "Nom visible")
        if not label:
            return
        category = simpledialog.askstring("Campagne", "Catégorie : food, tv, energie, electromenager, services...")
        if not category:
            return

        camp = {
            "id": cid.strip().lower().replace(" ", "_"),
            "label": label,
            "category": category,
            "intent": "product_category",
            "product_id": "",
            "product_query": "",
            "keywords": [],
            "hashes": []
        }

        self.campaigns_data.setdefault("campaigns", []).append(camp)
        save(CAMPAIGNS, self.campaigns_data)
        self.reload_all()

    def save_food_menu(self):
        lines = self.food_text.get("1.0", "end").splitlines()
        items = []
        for line in lines:
            if "|" in line:
                name, price = line.split("|", 1)
                name = name.strip()
                price = price.strip()
                if name and price:
                    items.append({"name": name, "price": price})

        self.sales_data.setdefault("food", {})["items"] = items
        save(SALES, self.sales_data)
        messagebox.showinfo("OK", "Menu sauvegardé.")

    def save_catalog(self):
        txt = self.catalog_text.get("1.0", "end").strip()
        self.sales_data.setdefault("non_food", {})["catalog_overview"] = txt
        save(SALES, self.sales_data)
        messagebox.showinfo("OK", "Réponse catalogue sauvegardée.")

    def select_campaign_json(self, event=None):
        sel = self.campaign_list.curselection()
        if not sel:
            return
        camp = self.campaigns_data.get("campaigns", [])[sel[0]]
        self.campaign_json_text.delete("1.0", "end")
        self.campaign_json_text.insert("end", json.dumps(camp, ensure_ascii=False, indent=2))

    def new_campaign_json(self):
        camp = {
            "id": "nouvelle_campagne",
            "label": "Nouvelle campagne",
            "category": "services",
            "intent": "product_category",
            "product_id": "",
            "product_query": "",
            "keywords": [],
            "hashes": []
        }
        self.campaign_json_text.delete("1.0", "end")
        self.campaign_json_text.insert("end", json.dumps(camp, ensure_ascii=False, indent=2))

    def save_campaign_json(self):
        raw = self.campaign_json_text.get("1.0", "end").strip()
        try:
            camp = json.loads(raw)
        except Exception as e:
            messagebox.showerror("Erreur JSON", str(e))
            return

        campaigns = self.campaigns_data.setdefault("campaigns", [])
        cid = camp.get("id")
        replaced = False

        for i, c in enumerate(campaigns):
            if c.get("id") == cid:
                campaigns[i] = camp
                replaced = True
                break

        if not replaced:
            campaigns.append(camp)

        save(CAMPAIGNS, self.campaigns_data)
        messagebox.showinfo("OK", "Campagne sauvegardée.")
        self.reload_all()

if __name__ == "__main__":
    app = Admin()
    app.mainloop()
