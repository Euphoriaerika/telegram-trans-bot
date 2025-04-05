import logging
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from database import insert_transaction

logger = logging.getLogger(__name__)

# Визначення станів розмови
CHOOSING, DESCRIPTION, TYPE, CATEGORY, AMOUNT = range(5)

# Словник для маппінгу
BUTTON_MAPPING = {
    "📉 Витрати": "витрати",
    "📈 Надходження": "надходження",
    "🚫 Відміна": "відміна",
    "💵 Заробітна платня/Пенсія": "заробітна платня/пенсія",
    "💰 Інше": "інше",
    "📦 Продукти": "продукти",
    "🎉 Розваги": "розваги",
    "🚕 Транспорт": "транспорт",
    "👚 Одяг": "одяг",
    "🏠 Для дому": "дім та побут",
    "💊 Здоров'я": "медичні послуги",
    "📚 Освіта": "освіта",
    "✈️ Подорожі": "подорожі",
    "💡 Комуналка": "комунальні послуги",
}


async def delete_last_prompt(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Видаляє попередню бот-підказку, якщо вона збережена."""
    chat_id = update.effective_chat.id
    last_id = context.user_data.get("last_prompt_message_id")
    if last_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=last_id)
        except Exception as e:
            logger.error(f"Помилка при видаленні повідомлення {last_id}: {e}")
        context.user_data["last_prompt_message_id"] = None


# Обробка команди /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    sent_message = await update.message.reply_text(
        "Вітаю! Оберіть дію:",
        reply_markup=ReplyKeyboardMarkup(
            [["➕ Додати транзакцію"]], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return CHOOSING


# Обробка команди /add (початок введення транзакції)
async def add_transaction(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Видаляємо попереднє повідомлення
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення користувача: {e}")
    await delete_last_prompt(update, context)

    # Показуємо клавіатуру з описом
    sent_message = await update.message.reply_text(
        "Введіть опис транзакції:",
        reply_markup=ReplyKeyboardMarkup(
            [["🚫 Відміна"]], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return DESCRIPTION


# Обробка опису транзакції
async def description_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    # Зберігаємо введений опис
    context.user_data["description"] = update.message.text

    # Видаляємо попереднє повідомлення
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення користувача: {e}")
    await delete_last_prompt(update, context)

    # Показуємо клавіатуру з типом транзакції
    sent_message = await update.message.reply_text(
        "Оберіть тип транзакції:",
        reply_markup=ReplyKeyboardMarkup(
            [["📉 Витрати", "📈 Надходження"], ["🚫 Відміна"]],
            one_time_keyboard=True,
            resize_keyboard=True,
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return TYPE


# Обробка типу транзакції
async def type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Зберігаємо введений тип
    selected_type = update.message.text
    context.user_data["type"] = BUTTON_MAPPING[selected_type]

    # Видаляємо попереднє повідомлення
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення користувача: {e}")
    await delete_last_prompt(update, context)

    # Показуємо клавіатуру з категоріями транзакції
    if selected_type == "📈 Надходження":
        reply_keyboard = [["💵 Заробітна платня/Пенсія", "💰 Інше"], ["🚫 Відміна"]]
    elif selected_type == "📉 Витрати":
        reply_keyboard = [
            ["📦 Продукти", "🎉 Розваги", "🚕 Транспорт"],
            ["👚 Одяг", "🏠 Для дому", "💊 Здоров'я"],
            ["📚 Освіта", "✈️ Подорожі", "💡 Комуналка"],
            ["🚫 Відміна"],
        ]
    else:
        await update.message.reply_text("Невірний вибір типу транзакції.")
        return ConversationHandler.END

    sent_message = await update.message.reply_text(
        "Оберіть категорію транзакції:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return CATEGORY


# Обробка типу транзакції
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Зберігаємо введений тип
    context.user_data["category"] = BUTTON_MAPPING[update.message.text]

    # Видаляємо попереднє повідомлення
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення користувача: {e}")
    await delete_last_prompt(update, context)

    # Показуємо клавіатуру з сумою транзакції
    sent_message = await update.message.reply_text(
        "Введіть суму транзакції (числове значення):",
        reply_markup=ReplyKeyboardMarkup(
            [["🚫 Відміна"]], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return AMOUNT


# Обробка суми транзакції
async def amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Конвертуємо введену суму у числове значення
    try:
        amount = float(update.message.text)
    except ValueError:
        # Видаляємо попереднє повідомлення
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Не вдалося видалити повідомлення користувача: {e}")

        # Повідомлення про повторне введення
        sent_message = await update.message.reply_text(
            "Будь ласка, введіть числове значення для суми:"
        )
        context.user_data["last_prompt_message_id"] = sent_message.message_id
        return AMOUNT
    # Зберігаємо введену суму
    context.user_data["amount"] = amount

    # Видаляємо попереднє повідомлення
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення користувача: {e}")
    await delete_last_prompt(update, context)

    context.user_data["date"] = datetime.now().strftime("%Y-%m-%d")
    # Формування документа транзакції
    transaction = {
        "date": context.user_data["date"],
        "description": context.user_data["description"],
        "category": context.user_data["category"],
        "type": context.user_data["type"],
        "amount": context.user_data["amount"],
        "user": (
            update.message.from_user.username
            if update.message.from_user.username
            else update.message.from_user.first_name
        ),
    }

    success, result_or_error = insert_transaction(transaction)
    await delete_last_prompt(update, context)
    if success:
        sent_message = await update.message.reply_text(
            "Транзакція записана! Ідентифікатор: " + result_or_error
        )
    else:
        sent_message = await update.message.reply_text(
            "Помилка запису транзакції: " + result_or_error
        )
    context.user_data["last_prompt_message_id"] = sent_message.message_id

    # Відправляємо меню для подальших дій
    reply_keyboard = [["➕ Додати транзакцію"]]
    sent_message = await update.message.reply_text(
        "Вітаю! Оберіть дію:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return CHOOSING


# Обробка команди /cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    # Видаляємо попереднє повідомлення
    try:
        await update.message.delete()
    except Exception as e:
        logger.error(f"Не вдалося видалити повідомлення користувача: {e}")
    await delete_last_prompt(update, context)

    # Потім надсилаємо меню, як у /start
    reply_keyboard = [["➕ Додати транзакцію"]]
    sent_message = await update.message.reply_text(
        "Вітаю! Оберіть дію:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    context.user_data["last_prompt_message_id"] = sent_message.message_id
    return CHOOSING


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        CHOOSING: [
            MessageHandler(filters.Regex("^🚫 Відміна$"), cancel),
            MessageHandler(filters.Regex("^➕ Додати транзакцію$"), add_transaction),
        ],
        DESCRIPTION: [
            MessageHandler(filters.Regex("^🚫 Відміна$"), cancel),
            MessageHandler(filters.TEXT & ~filters.COMMAND, description_handler),
        ],
        TYPE: [
            MessageHandler(filters.Regex("^🚫 Відміна$"), cancel),
            MessageHandler(
                filters.Regex("^(📉 Витрати|📈 Надходження)$"), type_handler
            ),
        ],
        CATEGORY: [
            MessageHandler(filters.Regex("^🚫 Відміна$"), cancel),
            MessageHandler(
                filters.Regex(
                    "^(💵 Заробітна платня/Пенсія|💰 Інше|📦 Продукти|🎉 Розваги|🚕 Транспорт|👚 Одяг|🏠 Для дому|💊 Здоров'я|📚 Освіта|✈️ Подорожі|💡 Комуналка)$"
                ),
                category_handler,
            ),
        ],
        AMOUNT: [
            MessageHandler(filters.Regex("^🚫 Відміна$"), cancel),
            MessageHandler(filters.TEXT & ~filters.COMMAND, amount_handler),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
