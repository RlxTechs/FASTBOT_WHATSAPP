from pathlib import Path

files = [
    "main.py",
    "bot_core.py",
    "chrome_control.py",
    "campaign_context.py",
    "intent_bank.py",
    "sales_orchestrator.py",
    "smart_reply.py",
    "admin_sales_gui.py",
    "admin_campaign_gui.py",
    "campaign_admin.py",
    "learning_admin.py"
]

for name in files:
    p = Path(name)
    if not p.exists():
        continue

    txt = p.read_text(encoding="utf-8-sig")
    txt = txt.replace("BASE_DIR = Path(__file__).resolve().parent", "from app_paths import BASE_DIR")
    p.write_text(txt, encoding="utf-8")

print("OK - chemins compatibles source + EXE")
