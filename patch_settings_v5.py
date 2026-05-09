import json
from pathlib import Path

p = Path("settings.json")
data = json.loads(p.read_text(encoding="utf-8-sig")) if p.exists() else {}

data["business_name"] = "O'CG / BZ STORE"
data["city"] = "Brazzaville"
data["whatsapp"] = "+242050541963"
data["phone"] = "+242066518669"

data["send_automatically"] = True
data["auto_send_only_safe"] = True
data["confidence_required"] = 0.88
data["auto_send_delay_seconds"] = 0.6
data["skip_if_message_box_not_empty"] = True
data["poll_seconds"] = 1.5
data["debug_enabled"] = True

data.setdefault("chrome_control", {})
data["chrome_control"]["enabled"] = True
data["chrome_control"]["debug_port"] = 9222
data["chrome_control"]["attach_if_available"] = True
data["chrome_control"]["auto_launch_if_not_available"] = True
data["chrome_control"]["use_dedicated_profile"] = True
data["chrome_control"]["dedicated_profile_dir"] = "chrome_whatsapp_profile"
data["chrome_control"]["whatsapp_url"] = "https://web.whatsapp.com/"
data["chrome_control"]["wait_ready_seconds"] = 240

data["safe_auto_intents"] = [
  "campaign_context_reply",
  "food_context_delivery_menu",
  "food_context_location_delivery",
  "food_context_order",
  "product_single",
  "product_variant",
  "product_tv_size",
  "product_tv_overview",
  "product_brand_overview",
  "delivery",
  "delivery_zone",
  "city_location",
  "contact",
  "payment_info",
  "order_info",
  "bank_delivery_question",
  "bank_location_question",
  "bank_payment_question",
  "bank_order_start",
  "bank_price_final",
  "bank_warranty_question",
  "bank_new_or_used",
  "bank_opening_hours",
  "bank_trust_reassurance",
  "bank_bulk_or_wholesale",
  "bank_compare_models"
]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print("settings.json optimisé V5.")
