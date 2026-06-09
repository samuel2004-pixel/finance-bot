from telegram import Update
from telegram.ext import ContextTypes


async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await help_command(update, context)


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    text = (
        "❓ Command Reference\n\n"
        "📅 /startday — Reset all values for the day\n\n"
        "💰 +amount — Add a receipt in rubles (e.g. +15000)\n\n"
        "💰 +0 — Show session total (since last clear)\n\n"
        "➖ -amount — Cancel a mistaken receipt (e.g. -15000)\n\n"
        "💸 /deduction amount — Record a payment sent in $ (e.g. /deduction 650)\n\n"
        "✅ /clear(amount) — Clear part of the debt in $ (e.g. /clear(500) or /clear 500)\n\n"
        "💱 /rate value — Set exchange rate (e.g. /rate 91.2)\n\n"
        "📈 /markup value — Set markup percentage (e.g. /markup 7)\n\n"
        "📊 /stat — Show today's statistics\n\n"
        "❓ /help — Show this help"
    )
    await update.message.reply_text(text)