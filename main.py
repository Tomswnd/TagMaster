from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes, CommandHandler, CallbackQueryHandler
from bot_logic.commands import create_category_command, join_category_command, list_categories_command, \
    add_user_command, delete_category_command, handle_delete_callback, info_command
from bot_logic.handlers import mention_handler

TOKEN = "8561051025:AAHDeO3pw4-0ek25LCUnlXYM2-LKLtH96Ms"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ciao! Il bot è attivo. Creato da @ityttmom su Telegram.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()



    app.add_handler(CommandHandler("start", start))
    # app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, mention_handler))

    app.add_handler(CommandHandler("info", info_command))
    app.add_handler(CommandHandler("creacategoria", create_category_command))
    app.add_handler(CommandHandler("iscrivi", join_category_command))
    app.add_handler(CommandHandler("listacategorie",list_categories_command ))
    app.add_handler(CommandHandler("aggiungi", add_user_command ))
    app.add_handler(CommandHandler("eliminacategoria", delete_category_command))
    app.add_handler(CallbackQueryHandler(handle_delete_callback, pattern="^(confirm_delete|cancel_delete)"))


    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, mention_handler))



    print("Bot in esecuzione...")
    app.run_polling()

if __name__ == "__main__":
    main()