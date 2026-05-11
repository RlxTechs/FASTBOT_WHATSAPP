from chrome_control import attach_driver, ensure_whatsapp_tab, wait_for_whatsapp_ready
from autonomous_patrol import snapshot_chat_rows

driver = attach_driver()
ensure_whatsapp_tab(driver)
wait_for_whatsapp_ready(driver)

rows = snapshot_chat_rows(driver)

print("=" * 90)
print("DIAGNOSTIC PATROUILLE LIVE")
print("=" * 90)
print("Conversations détectées :", len(rows))
print()

for r in rows[:15]:
    print("-" * 90)
    print("Index   :", r["index"])
    print("Titre   :", r["title"])
    print("Unread  :", r["unread"])
    print("Hash    :", r["preview_hash"])
    print("Aperçu  :")
    print(r["text"][:500])
