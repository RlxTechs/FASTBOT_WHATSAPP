from pathlib import Path

p = Path("media_engine.py")
txt = p.read_text(encoding="utf-8-sig")

old = '''def select_media_for_reply(message: str, chat_id: str, result: Dict[str, Any]) -> List[str]:
    data = media_data()
    if not data.get("enabled", True):
        return []'''

new = '''def select_media_for_reply(message: str, chat_id: str, result: Dict[str, Any]) -> List[str]:
    # Priorité V6.0 : images officielles directement retournées depuis products.json
    direct_images = result.get("_media_images") or []
    if direct_images:
        clean = []
        for img in direct_images:
            p = Path(str(img))
            if p.exists() and p.is_file() and str(p.resolve()) not in clean:
                clean.append(str(p.resolve()))
        if clean:
            return clean[: int(media_data().get("max_images_per_reply", 3))]

    data = media_data()
    if not data.get("enabled", True):
        return []'''

if old in txt:
    txt = txt.replace(old, new)
else:
    print("⚠️ Fonction select_media_for_reply non trouvée exactement.")

p.write_text(txt, encoding="utf-8")
print("✅ media_engine.py priorise maintenant products.json.")
