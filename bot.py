from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8561051025:AAHDeO3pw4-0ek25LCUnlXYM2-LKLtH96Ms"

async def handle_mentions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if "@" in text:
        await update.message.reply_text("Hai menzionato qualcuno!")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, handle_mentions))
#first commit
app.run_polling()
