from app.management.commands.bot import bot


@bot.message_handler(commands=['admin'])
def admin_message(message):
    bot.send_message(message.chat.id, 'admin')
