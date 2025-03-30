import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from handlers import (
    start,
    add_transaction,
    description_handler,
    category_handler,
    type_handler,
    amount_handler,
    cancel,
    CHOOSING,
    DESCRIPTION,
    CATEGORY,
    TYPE,
    AMOUNT,
)

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING: [
                MessageHandler(filters.Regex("^Відміна$"), cancel),
                MessageHandler(filters.Regex("^Додати транзакцію$"), add_transaction),
            ],
            DESCRIPTION: [
                MessageHandler(filters.Regex("^Відміна$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, description_handler),
            ],
            CATEGORY: [
                MessageHandler(filters.Regex("^Відміна$"), cancel),
                MessageHandler(filters.Regex("^(продукти|розваги)$"), category_handler),
            ],
            TYPE: [
                MessageHandler(filters.Regex("^Відміна$"), cancel),
                MessageHandler(filters.Regex("^(витрати|надходження)$"), type_handler),
            ],
            AMOUNT: [
                MessageHandler(filters.Regex("^Відміна$"), cancel),
                MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
