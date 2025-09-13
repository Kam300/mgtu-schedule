import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Замените на ваш токен бота
BOT_TOKEN = "7808052232:AAEe0RDB5JLwxFCEAsjw8NE02RSB8yxMwMw"  # Получите токен у @BotFather
# Замените на URL вашего размещенного приложения
WEB_APP_URL = "https://mgtu-schedule.onrender.com"  # Ваш URL на Render


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
                f"Найдено файлов: {files_count}\n\n"
                f"💡 Используйте кнопки 'Скачать' в приложении для загрузки файлов."
            )
        elif app_data.get('action') == 'file_downloaded':
            filename = app_data.get('filename', 'файл')
            await update.message.reply_text(
                f"📥 Файл '{filename}' успешно загружен!\n"
                f"🔍 Проверьте папку загрузок вашего устройства."
            )
        elif app_data.get('action') == 'request_file':
            file_index = app_data.get('file_index')
            user_id = app_data.get('user_id')
            
            if file_index is not None:
                # Send file to user
                try:
                    import requests
                    download_url = f"{WEB_APP_URL}/download/{file_index}"
                    
                    await update.message.reply_text(
                        f"📤 Отправляю файл...\n"
                        f"🔗 Ссылка для скачивания: {download_url}\n\n"
                        f"💡 Нажмите на ссылку, чтобы скачать файл."
                    )
                except Exception as e:
                    logger.error(f"Ошибка при отправке файла: {e}")
                    await update.message.reply_text(
                        f"❌ Ошибка при получении файла.\n"
                        f"🔗 Попробуйте скачать напрямую: {WEB_APP_URL}/download/{file_index}"
                    )
    except Exception as e:
        logger.error(f"Ошибка обработки данных WebApp: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке данных из приложения."
        )


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
