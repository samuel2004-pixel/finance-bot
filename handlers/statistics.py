from telegram import Update
from telegram.ext import ContextTypes

from database import (
    get_receipts_total,
    get_rate,
    get_markup,
    get_total_deductions,
    get_total_cleared
)

from services.calculator import (
    calculate_markup_amount,
    calculate_net_rub,
    calculate_usdt
)


async def stat_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    chat_id = update.effective_chat.id

    total_rub   = get_receipts_total(chat_id)
    rate        = get_rate(chat_id)
    markup      = get_markup(chat_id)
    deductions  = get_total_deductions(chat_id)
    cleared     = get_total_cleared(chat_id)

    markup_amount = calculate_markup_amount(total_rub, markup)
    net_rub       = calculate_net_rub(total_rub, markup)
    usdt          = calculate_usdt(net_rub, rate)
    remaining     = usdt - deductions - cleared

    text = (
        f"📊 Statistics\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 Total RUB:\n"
        f"{total_rub:,.2f} ₽\n\n"
        f"📈 Markup: {markup:.2f}%\n"
        f"💸 Markup Amount:\n"
        f"{markup_amount:,.2f} ₽\n\n"
        f"💰 Net RUB:\n"
        f"{net_rub:,.2f} ₽\n\n"
        f"💱 Rate: {rate}\n\n"
        f"🪙 USDT Debt:\n"
        f"{usdt:,.2f}$\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"💸 Payments Sent:\n"
        f"{deductions:,.2f}$\n\n"
        f"✅ Cleared:\n"
        f"{cleared:,.2f}$\n\n"
        f"🏦 Remaining Debt:\n"
        f"{remaining:,.2f}$"
    )

    await update.message.reply_text(text)