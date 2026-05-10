import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path

from media_engine import explain_media_selection

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

MEDIA = BASE_DIR / "media_catalog.json"
ASSETS = BASE_DIR / "assets"

def load():
    if MEDIA.exists():
        data = json.loads(MEDIA.read_text(encoding="utf-8-sig"))
    else:
        data = {}

    data.setdefault("version", "6.2")
    data.setdefault("enabled", True)
    data.setdefault("send_images_automatically", True)
    data.setdefault("max_images_per_reply", 3)
    data.setdefault("strict_mode", True)
    data.setdefault("bundles", [])
    return data

def save(data):
    MEDIA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def split_csv(text):
    return [x.strip() for x in text.replace("\n", ",").split(",") if x.strip()]

class MediaAdmin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCG Bot — Admin Médias Produits V6.2")
        self.geometry("1250x760")
        self.minsize(1100, 680)
        self.data = load()
        self.selected_index = None
        self.build()
        self.refresh()

    def build(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        top = ttk.Frame(root)
        top.pack(fill="x", pady=(0, 8))

        self.enabled_var = tk.BooleanVar(value=True)
        self.auto_var = tk.BooleanVar(value=True)
        self.strict_var = tk.BooleanVar(value=True)
        self.global_max_var = tk.StringVar(value="3")

        ttk.Checkbutton(top, text="Médias activés", variable=self.enabled_var).pack(side="left", padx=5)
        ttk.Checkbutton(top, text="Envoi images automatique", variable=self.auto_var).pack(side="left", padx=5)
        ttk.Checkbutton(top, text="Mode strict anti-erreur", variable=self.strict_var).pack(side="left", padx=5)
        ttk.Label(top, text="Max images/réponse").pack(side="left", padx=(20, 5))
        ttk.Entry(top, textvariable=self.global_max_var, width=5).pack(side="left")
        ttk.Button(top, text="Sauvegarder config globale", command=self.save_global).pack(side="left", padx=10)

        body = ttk.PanedWindow(root, orient="horizontal")
        body.pack(fill="both", expand=True)

        left = ttk.Frame(body)
        body.add(left, weight=1)

        center = ttk.Frame(body)
        body.add(center, weight=2)

        right = ttk.Frame(body)
        body.add(right, weight=2)

        ttk.Label(left, text="Bundles médias", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.listbox = tk.Listbox(left, width=40, height=30)
        self.listbox.pack(fill="both", expand=True, pady=8)
        self.listbox.bind("<<ListboxSelect>>", self.select_bundle)

        ttk.Button(left, text="Nouveau bundle", command=self.new_bundle).pack(fill="x", pady=2)
        ttk.Button(left, text="Dupliquer", command=self.duplicate_bundle).pack(fill="x", pady=2)
        ttk.Button(left, text="Activer / Désactiver", command=self.toggle_active).pack(fill="x", pady=2)
        ttk.Button(left, text="Supprimer", command=self.delete_bundle).pack(fill="x", pady=2)
        ttk.Button(left, text="Recharger", command=self.refresh).pack(fill="x", pady=2)

        ttk.Label(center, text="Réglages du bundle", font=("Segoe UI", 12, "bold")).pack(anchor="w")

        form = ttk.Frame(center)
        form.pack(fill="x", pady=5)

        self.active_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Actif", variable=self.active_var).grid(row=0, column=0, sticky="w")

        ttk.Label(form, text="ID").grid(row=1, column=0, sticky="w")
        self.id_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.id_var).grid(row=1, column=1, sticky="ew")

        ttk.Label(form, text="Label").grid(row=2, column=0, sticky="w")
        self.label_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.label_var).grid(row=2, column=1, sticky="ew")

        ttk.Label(form, text="Max images").grid(row=3, column=0, sticky="w")
        self.max_var = tk.StringVar(value="3")
        ttk.Entry(form, textvariable=self.max_var).grid(row=3, column=1, sticky="ew")

        ttk.Label(form, text="Score minimum").grid(row=4, column=0, sticky="w")
        self.min_score_var = tk.StringVar(value="15")
        ttk.Entry(form, textvariable=self.min_score_var).grid(row=4, column=1, sticky="ew")

        ttk.Label(form, text="Priorité").grid(row=5, column=0, sticky="w")
        self.priority_var = tk.StringVar(value="0")
        ttk.Entry(form, textvariable=self.priority_var).grid(row=5, column=1, sticky="ew")

        self.allow_context_var = tk.BooleanVar(value=False)
        self.allow_intent_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="Autoriser contexte seul", variable=self.allow_context_var).grid(row=6, column=0, sticky="w")
        ttk.Checkbutton(form, text="Autoriser intent seul", variable=self.allow_intent_var).grid(row=6, column=1, sticky="w")

        form.columnconfigure(1, weight=1)

        ttk.Label(center, text="Mots-clés déclencheurs. Exemple : frigo, réfrigérateur").pack(anchor="w", pady=(8,0))
        self.keywords_text = tk.Text(center, height=4)
        self.keywords_text.pack(fill="x")

        ttk.Label(center, text="Mots-clés négatifs. Si le client dit ces mots, aucune image de ce bundle.").pack(anchor="w", pady=(8,0))
        self.negative_text = tk.Text(center, height=3)
        self.negative_text.pack(fill="x")

        ttk.Label(center, text="Contextes autorisés. Exemple : refrigerateur, iphones, food").pack(anchor="w", pady=(8,0))
        self.contexts_text = tk.Text(center, height=3)
        self.contexts_text.pack(fill="x")

        ttk.Label(center, text="Intents autorisés. Optionnel.").pack(anchor="w", pady=(8,0))
        self.intents_text = tk.Text(center, height=3)
        self.intents_text.pack(fill="x")

        ttk.Label(center, text="Images associées, une par ligne").pack(anchor="w", pady=(8,0))
        self.images_text = tk.Text(center, height=8)
        self.images_text.pack(fill="both", expand=True)

        img_btns = ttk.Frame(center)
        img_btns.pack(fill="x", pady=5)
        ttk.Button(img_btns, text="Ajouter images", command=self.add_images).pack(side="left", padx=3)
        ttk.Button(img_btns, text="Nettoyer images inexistantes", command=self.clean_missing_images).pack(side="left", padx=3)
        ttk.Button(img_btns, text="Sauvegarder bundle", command=self.save_bundle).pack(side="left", padx=3)

        ttk.Label(right, text="Test / Diagnostic", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        ttk.Label(right, text="Message client à tester").pack(anchor="w")
        self.test_msg = tk.Text(right, height=5)
        self.test_msg.pack(fill="x", pady=5)
        self.test_msg.insert("end", "Les iPhone la c'est combien")

        ttk.Label(right, text="Intent simulé").pack(anchor="w")
        self.test_intent_var = tk.StringVar(value="product_category_iphones_prices")
        ttk.Entry(right, textvariable=self.test_intent_var).pack(fill="x", pady=5)

        ttk.Button(right, text="Tester sélection média", command=self.run_test).pack(fill="x", pady=5)

        self.result_text = tk.Text(right, wrap="word")
        self.result_text.pack(fill="both", expand=True)

    def refresh(self):
        self.data = load()
        self.enabled_var.set(bool(self.data.get("enabled", True)))
        self.auto_var.set(bool(self.data.get("send_images_automatically", True)))
        self.strict_var.set(bool(self.data.get("strict_mode", True)))
        self.global_max_var.set(str(self.data.get("max_images_per_reply", 3)))

        self.listbox.delete(0, "end")
        for b in self.data.get("bundles", []):
            status = "✅" if b.get("active", True) else "⛔"
            self.listbox.insert("end", f"{status} {b.get('id')} — {b.get('label')}")

    def current_bundle(self):
        if self.selected_index is None:
            return None
        bundles = self.data.setdefault("bundles", [])
        if 0 <= self.selected_index < len(bundles):
            return bundles[self.selected_index]
        return None

    def select_bundle(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        self.selected_index = sel[0]
        b = self.current_bundle()
        if not b:
            return

        self.active_var.set(bool(b.get("active", True)))
        self.id_var.set(b.get("id", ""))
        self.label_var.set(b.get("label", ""))
        self.max_var.set(str(b.get("max_images", 3)))
        self.min_score_var.set(str(b.get("min_score", 15)))
        self.priority_var.set(str(b.get("priority", 0)))
        self.allow_context_var.set(bool(b.get("allow_context_only", False)))
        self.allow_intent_var.set(bool(b.get("allow_intent_only", False)))

        self.keywords_text.delete("1.0", "end")
        self.keywords_text.insert("end", ", ".join(b.get("keywords", [])))

        self.negative_text.delete("1.0", "end")
        self.negative_text.insert("end", ", ".join(b.get("negative_keywords", [])))

        self.contexts_text.delete("1.0", "end")
        self.contexts_text.insert("end", ", ".join(b.get("contexts", [])))

        self.intents_text.delete("1.0", "end")
        self.intents_text.insert("end", ", ".join(b.get("intents", [])))

        self.images_text.delete("1.0", "end")
        self.images_text.insert("end", "\n".join(b.get("image_paths", [])))

    def save_global(self):
        self.data["enabled"] = self.enabled_var.get()
        self.data["send_images_automatically"] = self.auto_var.get()
        self.data["strict_mode"] = self.strict_var.get()
        try:
            self.data["max_images_per_reply"] = int(self.global_max_var.get())
        except Exception:
            self.data["max_images_per_reply"] = 3
        save(self.data)
        messagebox.showinfo("OK", "Configuration globale sauvegardée.")

    def save_bundle(self):
        b = self.current_bundle()
        if not b:
            messagebox.showwarning("Attention", "Sélectionne un bundle.")
            return

        b["active"] = self.active_var.get()
        b["id"] = self.id_var.get().strip()
        b["label"] = self.label_var.get().strip()

        for field, var, default in [
            ("max_images", self.max_var, 3),
            ("min_score", self.min_score_var, 15),
            ("priority", self.priority_var, 0)
        ]:
            try:
                b[field] = int(var.get().strip())
            except Exception:
                b[field] = default

        b["allow_context_only"] = self.allow_context_var.get()
        b["allow_intent_only"] = self.allow_intent_var.get()
        b["keywords"] = split_csv(self.keywords_text.get("1.0", "end"))
        b["negative_keywords"] = split_csv(self.negative_text.get("1.0", "end"))
        b["contexts"] = split_csv(self.contexts_text.get("1.0", "end"))
        b["intents"] = split_csv(self.intents_text.get("1.0", "end"))
        b["image_paths"] = [x.strip() for x in self.images_text.get("1.0", "end").splitlines() if x.strip()]

        save(self.data)
        self.refresh()
        messagebox.showinfo("OK", "Bundle sauvegardé.")

    def new_bundle(self):
        bid = simpledialog.askstring("Nouveau bundle", "ID, ex: iphone_13, hamburger, frigo_82l")
        if not bid:
            return
        b = {
            "id": bid.strip().lower().replace(" ", "_"),
            "label": bid.strip(),
            "active": True,
            "keywords": [],
            "negative_keywords": [],
            "contexts": [],
            "intents": [],
            "image_paths": [],
            "max_images": 3,
            "min_score": 15,
            "priority": 0,
            "allow_context_only": False,
            "allow_intent_only": False
        }
        self.data.setdefault("bundles", []).append(b)
        save(self.data)
        self.refresh()

    def duplicate_bundle(self):
        b = self.current_bundle()
        if not b:
            return
        nb = json.loads(json.dumps(b, ensure_ascii=False))
        nb["id"] = nb.get("id", "bundle") + "_copie"
        nb["label"] = nb.get("label", "Bundle") + " copie"
        self.data.setdefault("bundles", []).append(nb)
        save(self.data)
        self.refresh()

    def toggle_active(self):
        b = self.current_bundle()
        if not b:
            return
        b["active"] = not bool(b.get("active", True))
        save(self.data)
        self.refresh()

    def delete_bundle(self):
        if self.selected_index is None:
            return
        if messagebox.askyesno("Supprimer", "Supprimer ce bundle ?"):
            self.data["bundles"].pop(self.selected_index)
            self.selected_index = None
            save(self.data)
            self.refresh()

    def add_images(self):
        b = self.current_bundle()
        if not b:
            messagebox.showwarning("Attention", "Sélectionne un bundle.")
            return

        files = filedialog.askopenfilenames(
            title="Choisir images",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp")]
        )
        if not files:
            return

        target = ASSETS / "custom" / (b.get("id") or "bundle")
        target.mkdir(parents=True, exist_ok=True)

        paths = b.setdefault("image_paths", [])
        for f in files:
            src = Path(f)
            dest = target / src.name
            shutil.copy2(src, dest)
            rel = dest.relative_to(BASE_DIR).as_posix()
            if rel not in paths:
                paths.append(rel)

        self.select_bundle()
        messagebox.showinfo("OK", "Images ajoutées.")

    def clean_missing_images(self):
        b = self.current_bundle()
        if not b:
            return
        kept = []
        removed = 0
        for p in b.get("image_paths", []):
            full = Path(p)
            if not full.is_absolute():
                full = BASE_DIR / p.replace("./", "")
            if full.exists():
                kept.append(p)
            else:
                removed += 1
        b["image_paths"] = kept
        save(self.data)
        self.select_bundle()
        messagebox.showinfo("OK", f"{removed} image(s) inexistante(s) retirée(s).")

    def run_test(self):
        msg = self.test_msg.get("1.0", "end").strip()
        intent = self.test_intent_var.get().strip()

        fake_result = {
            "intent": intent,
            "reply": "",
            "confidence": 0.9,
            "safe_to_auto_send": True
        }

        rows = explain_media_selection(msg, "admin_test", fake_result)
        self.result_text.delete("1.0", "end")

        self.result_text.insert("end", "DIAGNOSTIC MÉDIA\n")
        self.result_text.insert("end", "=" * 60 + "\n\n")

        for r in rows[:20]:
            self.result_text.insert("end", f"ID: {r.get('id', r.get('type'))}\n")
            self.result_text.insert("end", f"Label: {r.get('label', '')}\n")
            self.result_text.insert("end", f"Actif: {r.get('active', '')}\n")
            self.result_text.insert("end", f"Score: {r.get('score')}\n")
            self.result_text.insert("end", f"Raisons: {r.get('reasons', r.get('reason'))}\n")
            self.result_text.insert("end", f"Images trouvées: {r.get('images_found', len(r.get('images', [])))}\n")
            for img in r.get("images", [])[:5]:
                self.result_text.insert("end", f" - {img}\n")
            self.result_text.insert("end", "\n" + "-" * 60 + "\n\n")

if __name__ == "__main__":
    app = MediaAdmin()
    app.mainloop()
