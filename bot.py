import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Замените на ваш токен бота
BOT_TOKEN = ""
# Замените на URL вашего размещенного приложения
WEB_APP_URL = "http://localhost:5000"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет приветственное сообщение с кнопкой Mini App"""
    user = update.effective_user

    keyboard = [[
        InlineKeyboardButton(
            "📅 Открыть расписания",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_html(
        f"Привет, {user.mention_html()}! 👋\n\n"
        f"🎓 <b>Расписания СПО МГТУ</b>\n\n"
        f"Это приложение поможет тебе быстро найти и скачать:\n"
        f"• 📅 Расписания занятий 1 и 2 семестра\n"
        f"• 🔄 Замены в расписании\n"
        f"• 📊 Файлы всех отделений СПО\n\n"
        f"Нажми кнопку ниже, чтобы открыть приложение:",
        reply_markup=reply_markup
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет справочную информацию"""
    help_text = """
🆘 <b>Справка по боту</b>

<b>Команды:</b>
/start - Открыть главное меню
/help - Показать эту справку

<b>Возможности приложения:</b>
• 🔍 Поиск файлов расписаний по названию
• 📅 Сортировка замен по дате
• 📱 Удобный интерфейс для мобильных устройств
• ⬇️ Быстрое скачивание файлов Excel

<b>Источники данных:</b>
• Отделение №1 "Общеобразовательная подготовка"
• Отделение №2 "Информационных технологий и транспорта"  
• Отделение №3 "Строительства, экономики и сферы обслуживания"
• Замены для 1 и 2 семестров

Для работы с приложением нажми /start
    """

    await update.message.reply_html(help_text)


async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает данные, отправленные из Mini App"""
    data = update.effective_message.web_app_data.data

    try:
        import json
        app_data = json.loads(data)

        if app_data.get('action') == 'scan_completed':
            files_count = app_data.get('files_count', 0)
            await update.message.reply_text(
                f"✅ Сканирование завершено!\n"
                f"Найдено файлов: {files_count}"
            )
    except Exception as e:
        logger.error(f"Ошибка обработки данных WebApp: {e}")


def main() -> None:
    """Запуск бота"""
    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчик данных из WebApp
    application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_web_app_data))

    # Запускаем бота
    print("🤖 Telegram бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
