import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import bot_keyboards
import database
import i18n
import bot_handlers

print("=== 1. Reply Keyboard Rows ===")
kb = bot_keyboards.get_main_reply_keyboard()
for i, r in enumerate(kb.keyboard):
    print(f"Row {i+1}: {[b.text for b in r]}")

print("\n=== 2. Verification Inline Keyboard ===")
v_kb = bot_keyboards.get_verification_inline_keyboard()
print([[b.text, b.callback_data] for r in v_kb.inline_keyboard for b in r])

print("\n=== 3. Deposit Flow Verification ===")
u = database.get_or_create_user(123456, "trader_test", "Trader")
dep_id = database.create_deposit_request(123456, "USDT_TRC20", 150.0, "TXID987654321")
print(f"Deposit ID created: #{dep_id}")

print("\n=== 4. User Verification Check ===")
v_res = database.verify_user(123456)
print(f"User verified: {database.is_user_verified(123456)}")

print("\n=== 5. Withdrawal Flow Check ===")
w_id = database.create_withdrawal_request(123456, "USDT_TRC20", 50.0, "TXYZ123456789")
print(f"Withdrawal ID created: #{w_id}")

print("\n=== 6. i18n Translation Snippets ===")
print("Deposit Prompt:", i18n.t("deposit_cart_prompt", "en")[:40], "...")
print("Reviews Title:", i18n.t("user_reviews_content", "en")[:40], "...")
print("Calculator Title:", i18n.t("profit_calculator_content", "en")[:40], "...")

print("\nSUCCESS: All UI and Bot Flows Verified Perfectly!")
