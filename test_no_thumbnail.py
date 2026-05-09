from sales_orchestrator import generate_sales_reply

msg = "Bonjour ! Puis-je en savoir plus à ce sujet ?"
r = generate_sales_reply(msg, "test_no_thumbnail")

print("INTENT:", r.get("intent"))
print("CONF:", r.get("confidence"))
print("SAFE:", r.get("safe_to_auto_send"))
print("REPONSE:")
print(r.get("reply"))
