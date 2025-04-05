import logging
from telegram.ext import Application
from config import TELEGRAM_BOT_TOKEN
from handlers import conv_handler

# Налаштування логування
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == "__main__":
    main()
