import datetime
import logging

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

Token = "8652528784:AAGXSNemrtIpVlB8mz_OHtkPHp0PD4t_Bf4"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi there! I'm your bot. Use /help to see what I can do."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - welcome message\n"
        "/help - show this help message\n"
        "/echo <text> - repeat your text\n"
        "/time - show current server time\n"
        "/about - tell you about this bot"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args:
        text = " ".join(context.args)
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Usage: /echo <text>")

async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    await update.message.reply_text(f"Current server time: {now}")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "I am a simple Telegram bot built with python-telegram-bot and running from VS Code."
    )

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Sorry, I don't recognize that command. Use /help to see available commands."
    )

async def echo_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"You said: {update.message.text}")

app = ApplicationBuilder().token(Token).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(CommandHandler("time", time_command))
app.add_handler(CommandHandler("about", about))
app.add_handler(MessageHandler(filters.COMMAND, unknown_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_messages))

app.run_polling()

