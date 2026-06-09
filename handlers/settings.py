from telegram import Update
from telegram.ext import ContextTypes

from database import (
    set_rate,
    set_markup,
    add_deduction,
    add_cleared,
    reset_day,
    reset_session,
    get_total_deductions,
    get_total_cleared,
    get_receipts_total,
    get_session_total,
    get_session_count,
    get_rate,
    get_markup
)

from services.calculator import (
    calculate_markup_amount,
    calculate_net_rub,
    calculate_usdt
)


async def rate_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    try:
        rate = float(context.args[0])
        set_rate(chat_id, rate)
        await update.message.reply_text(
            f"💲 Exchange rate set to {rate:.4f}"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Usage:\n/rate 91.2")


async def markup_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    try:
        markup = float(context.args[0])
        set_markup(chat_id, markup)
        await update.message.reply_text(
            f"📈 Markup set to {markup:.0f}%"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Usage:\n/markup 7")


async def deduction_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    try:
        amount = float(context.args[0])
        add_deduction(chat_id, amount)
        total = get_total_deductions(chat_id)
        await update.message.reply_text(
            f"💸 Deduction Added\n\n"
            f"{amount:,.2f}$\n\n"
            f"Total Deductions: {total:,.2f}$"
        )
    except (IndexError, ValueError):
        await update.message.reply_text("Usage:\n/deduction 100")


async def clear_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    try:
        # Support both /clear 5 and /clear(5)
        raw = context.args[0].strip("()")
        amount = float(raw)
    except (IndexError, ValueError):
        await update.message.reply_text("Usage:\n/clear 100  or  /clear(100)")
        return

    add_cleared(chat_id, amount)
    reset_session(chat_id)   # reset session after each clear

    rate           = get_rate(chat_id)
    markup         = get_markup(chat_id)
    day_total      = get_receipts_total(chat_id)
    session_total  = get_session_total(chat_id)   # now 0 after reset
    session_count  = get_session_count(chat_id)   # now 0 after reset
    total_cleared  = get_total_cleared(chat_id)
    deductions     = get_total_deductions(chat_id)

    session_markup   = calculate_markup_amount(session_total, markup)
    session_with_mkp = session_total + session_markup
    day_net_rub      = calculate_net_rub(day_total, markup)
    day_usdt         = calculate_usdt(day_net_rub, rate)
    day_usdt_raw     = calculate_usdt(day_total, rate)
    remaining        = day_usdt - deductions - total_cleared

    await update.message.reply_text(
        f"✅ Cleared: {amount:,.2f}$\n"
        f"\n"
        f"🗒 Session total (since last clear):\n"
        f"• Receipts: {session_count}\n"
        f"• Total: {session_total:,.2f}₽ / {calculate_usdt(session_total, rate):,.2f}$\n"
        f"• Markup ({markup:.0f}%): +{session_markup:,.2f}₽\n"
        f"• With markup: {session_with_mkp:,.2f}₽\n"
        f"\n"
        f"🗒 Day total:\n"
        f"• Received: {day_total:,.2f}₽ / {day_usdt_raw:,.2f}$\n"
        f"• Total cleared: {total_cleared:,.2f}$\n"
        f"• Remaining debt: {remaining:,.2f}$"
    )

async def startday_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id
    reset_day(chat_id)
    await update.message.reply_text(
        "👋 Hello! I'm your financial tracking bot.\n\nType /help to see all commands."
    )
    await update.message.reply_text(
        "📅 Day has been reset. All today's data cleared."
    )