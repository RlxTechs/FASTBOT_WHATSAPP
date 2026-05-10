import json
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from pathlib import Path

try:
    from app_paths import BASE_DIR
except Exception:
    BASE_DIR = Path(__file__).resolve().parent

MEDIA = BASE_DIR / "media_catalog.json"
ASSETS = BASE_DIR / "assets"

def load():
    if MEDIA.exists():
        return json.loads(MEDIA.read_text(encoding="utf-8-sig"))
    return {"version": "5.9", "enabled": True, "send_images_automatically": True, "max_images_per_reply": 3, "bundles": []}

def save(data):
    MEDIA.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

class MediaAdmin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("OCG Bot — Admin Médias Produits")
        self.geometry("1050x680")
        self.data = load()
        self.selected_index = None
        self.build()
        self.refresh()

    def build(self):
        root = ttk.Frame(self, padding=10)
        root.pack(fill="both", expand=True)

        left = ttk.Frame(root)
        left.pack(side="left", fill="y", padx=(0,10))

        ttk.Label(left, text="Bundles médias", font=("Segoe UI", 12, "bold")).pack(anchor="w")
        self.listbox = tk.Listbox(left, width=35, height=28)
        self.listbox.pack(fill="y", expand=True, pady=8)
        self.listbox.bind("<<ListboxSelect>>", self.select_bundle)

        ttk.Button(left, text="Nouveau bundle", command=self.new_bundle).pack(fill="x", pady=2)
        ttk.Button(left, text="Supprimer", command=self.delete_bundle).pack(fill="x", pady=2)
        ttk.Button(left, text="Sauvegarder tout", command=self.save_current).pack(fill="x", pady=2)

        right = ttk.Frame(root)
        right.pack(side="left", fill="both", expand=True)

        form = ttk.Frame(right)
        form.pack(fill="x")

        ttk.Label(form, text="ID").grid(row=0, column=0, sticky="w")
        self.id_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.id_var).grid(row=0, column=1, sticky="ew")

        ttk.Label(form, text="Label").grid(row=1, column=0, sticky="w")
        self.label_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.label_var).grid(row=1, column=1, sticky="ew")

        ttk.Label(form, text="Max images").grid(row=2, column=0, sticky="w")
        self.max_var = tk.StringVar(value="3")
        ttk.Entry(form, textvariable=self.max_var).grid(row=2, column=1, sticky="ew")

        form.columnconfigure(1, weight=1)

        ttk.Label(right, text="Mots-clés, séparés par virgule").pack(anchor="w", pady=(10,0))
        self.keywords_text = tk.Text(right, height=3)
        self.keywords_text.pack(fill="x")

        ttk.Label(right, text="Contextes, séparés par virgule").pack(anchor="w", pady=(10,0))
        self.contexts_text = tk.Text(right, height=3)
        self.contexts_text.pack(fill="x")

        ttk.Label(right, text="Images associées").pack(anchor="w", pady=(10,0))
        self.images_text = tk.Text(right, height=10)
        self.images_text.pack(fill="both", expand=True)

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=8)

        ttk.Button(btns, text="Ajouter images", command=self.add_images).pack(side="left", padx=3)
        ttk.Button(btns, text="Sauvegarder bundle", command=self.save_bundle).pack(side="left", padx=3)
        ttk.Button(btns, text="Recharger", command=self.refresh).pack(side="left", padx=3)

    def refresh(self):
        self.data = load()
        self.listbox.delete(0, "end")
        for b in self.data.get("bundles", []):
            self.listbox.insert("end", f"{b.get('id')} — {b.get('label')}")

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

        self.id_var.set(b.get("id",""))
        self.label_var.set(b.get("label",""))
        self.max_var.set(str(b.get("max_images", 3)))

        self.keywords_text.delete("1.0", "end")
        self.keywords_text.insert("end", ", ".join(b.get("keywords", [])))

        self.contexts_text.delete("1.0", "end")
        self.contexts_text.insert("end", ", ".join(b.get("contexts", [])))

        self.images_text.delete("1.0", "end")
        self.images_text.insert("end", "\n".join(b.get("image_paths", [])))

    def new_bundle(self):
        bid = simpledialog.askstring("Nouveau bundle", "ID, ex: imprimante_epson_l3250")
        if not bid:
            return
        b = {
            "id": bid.strip().lower().replace(" ", "_"),
            "label": bid.strip(),
            "keywords": [],
            "contexts": [],
            "image_paths": [],
            "max_images": 3,
            "active": True
        }
        self.data.setdefault("bundles", []).append(b)
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

    def save_bundle(self):
        b = self.current_bundle()
        if not b:
            messagebox.showwarning("Attention", "Sélectionne un bundle.")
            return

        b["id"] = self.id_var.get().strip()
        b["label"] = self.label_var.get().strip()
        try:
            b["max_images"] = int(self.max_var.get().strip())
        except Exception:
            b["max_images"] = 3

        b["keywords"] = [x.strip() for x in self.keywords_text.get("1.0","end").replace("\n", ",").split(",") if x.strip()]
        b["contexts"] = [x.strip() for x in self.contexts_text.get("1.0","end").replace("\n", ",").split(",") if x.strip()]
        b["image_paths"] = [x.strip() for x in self.images_text.get("1.0","end").splitlines() if x.strip()]
        b["active"] = True

        save(self.data)
        self.refresh()
        messagebox.showinfo("OK", "Bundle sauvegardé.")

    def save_current(self):
        self.save_bundle()

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

        target_dir = ASSETS / "custom" / b.get("id", "bundle")
        target_dir.mkdir(parents=True, exist_ok=True)

        paths = b.setdefault("image_paths", [])

        for f in files:
            src = Path(f)
            dest = target_dir / src.name
            shutil.copy2(src, dest)
            rel = dest.relative_to(BASE_DIR).as_posix()
            if rel not in paths:
                paths.append(rel)

        self.select_bundle()
        messagebox.showinfo("OK", "Images ajoutées.")

if __name__ == "__main__":
    app = MediaAdmin()
    app.mainloop()
