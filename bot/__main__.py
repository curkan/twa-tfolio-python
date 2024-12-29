import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackContext, CallbackQueryHandler, ContextTypes, CommandHandler, MessageHandler, filters
from sqlalchemy import Date, and_, create_engine, extract, func, or_, select
from sqlalchemy.orm import sessionmaker



from bot.core.config import Settings, parse_settings
from bot.database.models.user import User
ALLOWED_USER_ID = 443472294

# Состояния
STATE_WAIT_FOR_BROADCAST = 'wait_for_broadcast'
STATE_WAIT_FOR_CONFIRMATION = 'wait_for_confirmation'

# Словарь для хранения состояний пользователей
user_states = {}
pending_messages = {}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_states[update.effective_user.id] = None
    keyboard = [
        [InlineKeyboardButton('Запустить tFolio', url='https://t.me/tfolio_bot/app')],
        [InlineKeyboardButton('Канал разработчика', url='https://t.me/tsurkan_hut')],
    ]

    await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Привет! Это бот tFolio - где можно бесплатно разместить свое портфолио прямо в телеграм и поделиться с клиентами в пару кликов. Нажмите ниже, чтобы попробовать.', reply_markup=InlineKeyboardMarkup(keyboard))

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Обнуляем состояние пользователя при старте
    user_states[update.effective_user.id] = None
    if update.effective_user.id == ALLOWED_USER_ID:
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Привет Чтобы начать рассылку, используйте команду /broadcast')

async def broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ALLOWED_USER_ID:
        user_states[update.effective_user.id] = STATE_WAIT_FOR_BROADCAST
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Режим рассылки включен. Отправьте сообщение для рассылки.')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ALLOWED_USER_ID and user_states[update.effective_user.id] == STATE_WAIT_FOR_BROADCAST:
        message = update.effective_message
        pending_messages[update.effective_user.id] = message
        user_states[update.effective_user.id] = STATE_WAIT_FOR_CONFIRMATION
        keyboard = [
            [InlineKeyboardButton('Подтвердить рассылку', callback_data='confirm_broadcast')],
            [InlineKeyboardButton('Отмена', callback_data='cancel_broadcast')]
        ]
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Подтвердите рассылку', reply_markup=InlineKeyboardMarkup(keyboard))

async def broadcast_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'confirm_broadcast':
        # Код для рассылки сообщения
        engine = create_engine(str(config.postgres.dsn))
        Session = sessionmaker(bind=engine)
        session = Session()
        query = select(User)
        users = session.scalars(query)
        message = pending_messages[update.effective_user.id]
        keyboard = [
            [InlineKeyboardButton('Запустить tFolio', url='https://t.me/tfolio_bot/app')],
        ]

        for user in users:
            try:
                print(f'Попытка отправки пользователю: {user.id}')
                if user != update.effective_user.id:
                    await context.bot.copy_message(chat_id=user.id, from_chat_id=message.chat_id, message_id=message.id, reply_markup=InlineKeyboardMarkup(keyboard))
                else:
                    await context.bot.send_message(chat_id=user.id, text=message.text, parse_mode=message.parse_mode, reply_markup=InlineKeyboardMarkup(keyboard))
            except Exception as e:
                print(f'Ошибка при отправке сообщения пользователю {user.id}: {e}')
        user_states[update.effective_user.id] = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Рассылка выполнена.')
    elif query.data == 'cancel_broadcast':
        user_states[update.effective_user.id] = None
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Рассылка отменена.')


if __name__ == '__main__':
    config: Settings = parse_settings()
    application = ApplicationBuilder().token(config.bot.token).build()
    
    start_handler = CommandHandler('start', start)
    menu_handler = CommandHandler('menu', menu)
    broadcast_command_handler = CommandHandler('broadcast', broadcast_command)
    broadcast_handler = MessageHandler(filters.ALL, broadcast)
    broadcast_confirmation_handler = CallbackQueryHandler(broadcast_confirmation)

    application.add_handler(start_handler)
    application.add_handler(menu_handler)
    application.add_handler(broadcast_command_handler)
    application.add_handler(broadcast_handler)
    application.add_handler(broadcast_confirmation_handler)

    application.run_polling()
