import textwrap
import re

with open('bot_handlers.py', encoding='utf-8') as f:
    content = f.read()

start = content.find('async def handle_callback_query')
end = content.find('\nasync def handle_withdraw_command', start)

func = content[start:end]

# 1. replace edit_message_text
func = func.replace('await query.edit_message_text(', 'await safe_edit(')

# 2. find the start of the `if data == ...` block
if_idx = func.find('\n    if data == "verify_and_activate":')

header = func[:if_idx]
body = func[if_idx:]

new_header = header.replace('    from telegram import InlineKeyboardButton, InlineKeyboardMarkup',
'''    import logging
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.error import BadRequest''')

safe_edit_def = '''
    # ── safe_edit: handles photo-message fallback & "not modified" errors ──
    async def safe_edit(text, reply_markup=None, parse_mode="Markdown"):
        try:
            await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except BadRequest as e:
            err = str(e)
            if "Message is not modified" in err:
                return  # Already showing same content — harmless
            if "There is no text in the message to edit" in err or "Message can't be edited" in err:
                # Photo/caption message — send a fresh reply instead
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            else:
                raise  # Re-raise for global handler
'''

# 3. Apply the replacements for set_mode, cycle_risk, cycle_exchange BEFORE indenting
OLD_SET_MODE = '''    elif data.startswith("set_mode:"):
        new_mode = data.split(":")[1]
        update_user_settings(user_id, trading_mode=new_mode)
        user["trading_mode"] = new_mode
        text = f"✅ Tryb handlu przełączony na *{new_mode.upper()}*!" if lang.startswith("pl") else f"✅ Trading mode switched to *{new_mode.upper()}*!"
        kb = [
            [InlineKeyboardButton(t("btn_settings", lang), callback_data="menu_settings")],
            [InlineKeyboardButton(t("btn_main_menu", lang), callback_data="menu_main")]
        ]
        await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")'''

NEW_SET_MODE = '''    elif data.startswith("set_mode:"):
        new_mode = data.split(":")[1]
        update_user_settings(user_id, trading_mode=new_mode)
        user["trading_mode"] = new_mode
        mode_icon = "⚡" if new_mode == "live" else "🧪"
        toast = f"{mode_icon} Mode: *{new_mode.upper()}* activated!" if not lang.startswith("pl") else f"{mode_icon} Tryb *{new_mode.upper()}* aktywowany!"
        await query.answer(toast, show_alert=True)
        # Re-display settings screen so user sees the change live
        text = format_settings_message(user, lang)
        keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
        await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")'''
body = body.replace(OLD_SET_MODE, NEW_SET_MODE, 1)

OLD_CYCLE_RISK = '''    elif data == "cycle_risk":
        current_risk = user.get("risk_percent", 2.0)
        next_risk = 5.0 if current_risk == 2.0 else (1.0 if current_risk == 5.0 else 2.0)
        update_user_settings(user_id, risk_percent=next_risk)
        user["risk_percent"] = next_risk
        text = f"✅ Ryzyko na transakcję: *{next_risk}%* salda." if lang.startswith("pl") else f"✅ Risk per trade set to *{next_risk}%* of account balance."
        kb = [[InlineKeyboardButton(t("btn_settings", lang), callback_data="menu_settings")]]
        await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")'''

NEW_CYCLE_RISK = '''    elif data == "cycle_risk":
        current_risk = user.get("risk_percent", 2.0)
        next_risk = 5.0 if current_risk == 2.0 else (1.0 if current_risk == 5.0 else 2.0)
        update_user_settings(user_id, risk_percent=next_risk)
        user["risk_percent"] = next_risk
        await query.answer(f"🎯 Risk set to {next_risk}%", show_alert=False)
        text = format_settings_message(user, lang)
        keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
        await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")'''
body = body.replace(OLD_CYCLE_RISK, NEW_CYCLE_RISK, 1)

OLD_CYCLE_EX = '''    elif data == "cycle_exchange":
        exchanges = ["binance", "bybit", "okx"]
        curr_idx = exchanges.index(user.get("exchange", "binance")) if user.get("exchange") in exchanges else 0
        next_ex = exchanges[(curr_idx + 1) % len(exchanges)]
        update_user_settings(user_id, exchange=next_ex)
        user["exchange"] = next_ex
        text = f"✅ Aktywna giełda: *{next_ex.upper()}*." if lang.startswith("pl") else f"✅ Active exchange set to *{next_ex.upper()}*."
        kb = [[InlineKeyboardButton(t("btn_settings", lang), callback_data="menu_settings")]]
        await safe_edit(text, reply_markup=InlineKeyboardMarkup(kb), parse_mode="Markdown")'''

NEW_CYCLE_EX = '''    elif data == "cycle_exchange":
        exchanges = ["binance", "bybit", "okx"]
        curr_idx = exchanges.index(user.get("exchange", "binance")) if user.get("exchange") in exchanges else 0
        next_ex = exchanges[(curr_idx + 1) % len(exchanges)]
        update_user_settings(user_id, exchange=next_ex)
        user["exchange"] = next_ex
        await query.answer(f"🔄 Exchange: {next_ex.upper()}", show_alert=False)
        text = format_settings_message(user, lang)
        keyboard = get_settings_keyboard(user["trading_mode"], user["risk_percent"], user["exchange"], lang=lang)
        await safe_edit(text, reply_markup=keyboard, parse_mode="Markdown")'''
body = body.replace(OLD_CYCLE_EX, NEW_CYCLE_EX, 1)

# Now indent body by 4 spaces
indented_body = textwrap.indent(body, '    ')

new_func = new_header + safe_edit_def + "\n    try:" + indented_body

# Add except block
new_func += '''
    except BadRequest as e:
        err = str(e)
        if "Message is not modified" not in err:
            logging.getLogger("AITradingBot").warning(f"Telegram BadRequest [{data}]: {e}")
            try:
                await query.answer(f"⚠️ Error: {err[:120]}", show_alert=True)
            except Exception:
                pass
    except Exception as e:
        logging.getLogger("AITradingBot").error(f"Callback error [{data}]: {e}", exc_info=True)
        try:
            await query.answer("⚠️ Something went wrong. Please try again.", show_alert=True)
        except Exception:
            pass
'''

new_content = content[:start] + new_func + content[end:]

with open('bot_handlers.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

import ast
try:
    ast.parse(new_content)
    print("Syntax OK!")
except SyntaxError as e:
    print(f"Syntax error: {e}")
