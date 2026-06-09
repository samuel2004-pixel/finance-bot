from telegram import Update
from telegram.ext import ContextTypes

from database import (
    add_receipt,
    remove_receipt,
    get_receipts_total,
    get_session_total,
    get_session_count,
    get_total_cleared,
    get_total_deductions,
    get_rate,
    get_markup
)

from services.calculator import (
    calculate_markup_amount,
    calculate_net_rub,
    calculate_usdt
)


async def amount_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    rate   = get_rate(chat_id)
    markup = get_markup(chat_id)

    # ── +0  Show session total ────────────────────────────
    if text == "+0":
        session_total  = get_session_total(chat_id)
        session_count  = get_session_count(chat_id)
        day_total      = get_receipts_total(chat_id)
        total_cleared  = get_total_cleared(chat_id)
        deductions     = get_total_deductions(chat_id)

        session_markup   = calculate_markup_amount(session_total, markup)
        session_with_mkp = session_total + session_markup
        day_net_rub      = calculate_net_rub(day_total, markup)
        day_usdt         = calculate_usdt(day_net_rub, rate)
        day_usdt_raw     = calculate_usdt(day_total, rate)
        card_markup      = calculate_markup_amount(session_total, markup)
        remaining        = day_usdt - deductions - total_cleared

        await update.message.reply_text(
            f"🗒 Session total (since last clear):\n"
            f"• Receipts: {session_count}\n"
            f"• Total: {session_total:,.2f}₽ / {calculate_usdt(session_total, rate):,.2f}$\n"
            f"• Markup ({markup:.0f}%): +{session_markup:,.2f}₽\n"
            f"• With markup: {session_with_mkp:,.2f}₽\n"
            f"\n"
            f"🗒 Day total:\n"
            f"• Received: {day_total:,.2f}₽ / {day_usdt_raw:,.2f}$\n"
            f"• Current card: {session_total:,.2f}₽\n"
            f"• Card markup ({markup:.0f}%): -{card_markup:,.2f}₽\n"
            f"• Total cleared: {total_cleared:,.2f}$\n"
            f"• Remaining debt: {remaining:,.2f}$"
        )
        return

    # ── +amount  Add receipt ──────────────────────────────
    if text.startswith("+"):
        try:
            amount = float(text[1:])
        except ValueError:
            await update.message.reply_text("Invalid amount.\n\nExample: +15000")
            return

        add_receipt(chat_id, amount)

        day_total      = get_receipts_total(chat_id)
        session_total  = get_session_total(chat_id)
        markup_amount  = calculate_markup_amount(amount, markup)
        card_markup    = calculate_markup_amount(session_total, markup)
        net_rub        = calculate_net_rub(day_total, markup)
        total_usdt     = calculate_usdt(net_rub, rate)
        day_usdt_raw   = calculate_usdt(day_total, rate)
        deductions     = get_total_deductions(chat_id)
        total_cleared  = get_total_cleared(chat_id)
        remaining      = total_usdt - deductions - total_cleared

        await update.message.reply_text(
            f"🧾 Receipt confirmed!\n"
            f"\n"
            f"🧾 Received: +{amount:,.2f}₽\n"
            f"📈 Markup ({markup:.0f}%): +{markup_amount:,.2f}₽\n"
            f"\n"
            f"🗒 Day total:\n"
            f"• Received: {day_total:,.2f}₽ / {day_usdt_raw:,.2f}$\n"
            f"• Current card: {session_total:,.2f}₽\n"
            f"• Card markup ({markup:.0f}%): -{card_markup:,.2f}₽\n"
            f"• Total USDT: {total_usdt:,.2f}$\n"
            f"• Now: {remaining:,.2f}$"
        )
        return

    # ── -amount  Cancel receipt ───────────────────────────
    if text.startswith("-"):
        try:
            amount = float(text[1:])
        except ValueError:
            await update.message.reply_text("Invalid amount.\n\nExample: -5000")
            return

        remove_receipt(chat_id, amount)
        day_total = get_receipts_total(chat_id)

        await update.message.reply_text(
            f"➖ Cancelled receipt: -{amount:,.2f}₽\n"
            f"Today's total: {day_total:,.2f}₽"
        )