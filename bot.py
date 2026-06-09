from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters
)

from config import BOT_TOKEN
from database import init_db

from handlers.start import start_command, help_command
from handlers.settings import (
    rate_command,
    markup_command,
    deduction_command,
    clear_command,
    startday_command
)
from handlers.statistics import stat_command
from handlers.transactions import amount_handler


def main():
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",     start_command))
    app.add_handler(CommandHandler("help",      help_command))
    app.add_handler(CommandHandler("rate",      rate_command))
    app.add_handler(CommandHandler("markup",    markup_command))
    app.add_handler(CommandHandler("deduction", deduction_command))
    app.add_handler(CommandHandler("clear",     clear_command))
    app.add_handler(CommandHandler("startday",  startday_command))
    app.add_handler(CommandHandler("stat",      stat_command))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            amount_handler
        )
    )

    print("Bot Started...")
    app.run_polling()


if __name__ == "__main__":
    main()