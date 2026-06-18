# Telegram → Gemini text bot

import os
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters
from google import genai

SCRIPT_DIR = Path(__file__).resolve().parent

env_candidates = [
    SCRIPT_DIR / ".env",
    SCRIPT_DIR / ".env.txt",
    SCRIPT_DIR / "env.txt",
    Path.cwd() / ".env",
    Path.cwd() / ".env.txt",
    Path.cwd() / "env.txt",
]

env_path = None
for candidate in env_candidates:
    if candidate.is_file():
        env_path = candidate
        break

if env_path is not None:
    load_dotenv(dotenv_path=env_path, override=False)
    print(f"Loaded env file: {env_path}")
else:
    print("No env file found. Checked:")
    for candidate in env_candidates:
        print(f"- {candidate}")

print("Current working directory:", Path.cwd())
print("Script directory:", SCRIPT_DIR)
print("Env file used:", env_path)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

print("TELEGRAM_TOKEN found:", bool(TELEGRAM_TOKEN))
print("GEMINI_API_KEY found:", bool(GEMINI_API_KEY))

if not TELEGRAM_TOKEN:
    raise RuntimeError(
        f"TELEGRAM_TOKEN not found. Checked env file: {env_path}"
    )

if not GEMINI_API_KEY:
    raise RuntimeError(
        f"GEMINI_API_KEY not found. Checked env file: {env_path}"
    )

application = Application.builder().token(TELEGRAM_TOKEN).build()
client = genai.Client(api_key=GEMINI_API_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! Send me a message and I'll ask Gemini."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Available commands:\n"
        "/start - welcome message\n"
        "/help - show this help\n\n"
        "How to use the bot:\n"
        "• Send a text message to ask Gemini for a reply.\n"
        "• Upload an image and I will give you a short summary first,\n"
        "  then you can choose to explore the main objects, mood, or context.\n"
        "• If Gemini is busy, please try the same request again in a moment."
    )

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))

async def ask_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt],
    )
    return response.text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if not text:
        return

    await update.message.reply_text("Thinking...")

    try:
        reply = await ask_gemini(text)
    except Exception as e:
        error_text = str(e)
        if "503" in error_text or "UNAVAILABLE" in error_text:
            reply = (
                "Gemini is temporarily busy right now. \n"
                "Please try the same message again in a moment."
            )
        else:
            reply = f"Gemini could not answer right now. Error: {error_text}"

    await update.message.reply_text(reply[:4000])

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    await update.message.reply_text("Analyzing the image...")

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    temp_path = SCRIPT_DIR / f"temp_{photo.file_id}.jpg"

    try:
        await file.download_to_drive(custom_path=temp_path)
        with Image.open(temp_path) as image:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    "Give a concise one-paragraph summary of this image. Focus on the main objects, mood, and context.",
                    image,
                ],
            )

        summary = response.text.strip()
        context.chat_data["last_image_summary"] = summary

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Main Objects",
                        callback_data="image_detail_main",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Mood",
                        callback_data="image_detail_mood",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Context",
                        callback_data="image_detail_context",
                    )
                ],
            ]
        )

        await update.message.reply_text(
            summary[:4000] +
            "\n\nWhich aspect would you like to explore further?",
            reply_markup=keyboard,
        )
    except Exception as e:
        await update.message.reply_text(f"Image analysis failed: {e}")
    finally:
        if temp_path.exists():
            temp_path.unlink()

async def handle_image_detail_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    choice = query.data or ""

    summary = context.chat_data.get("last_image_summary", "")
    if not summary:
        await query.edit_message_text(
            "No image summary is available yet. Please send a new image."
        )
        return

    prompts = {
        "image_detail_main": "Give me more information about the main objects in the image.",
        "image_detail_mood": "Explain the mood and atmosphere of the image in more detail.",
        "image_detail_context": "Explain the context and possible meaning of the image.",
    }

    prompt = prompts.get(choice, "Give me a bit more detail about this image.")

    await query.edit_message_text("Checking that detail now...")

    try:
        reply = await ask_gemini(
            f"Based on this image summary:\n{summary}\n\n{prompt}"
        )
        detail_text = reply[:4000]
        await query.message.reply_text(detail_text)

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Main Objects",
                        callback_data="image_detail_main",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Mood",
                        callback_data="image_detail_mood",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Context",
                        callback_data="image_detail_context",
                    )
                ],
            ]
        )
        await query.message.reply_text(
            "Would you like more detail about another aspect?",
            reply_markup=keyboard,
        )
    except Exception as e:
        await query.message.reply_text(f"Detail request failed: {e}")

application.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message,
    )
)
application.add_handler(
    MessageHandler(
        filters.PHOTO,
        handle_photo,
    )
)
application.add_handler(
    CallbackQueryHandler(
        handle_image_detail_callback,
        pattern="^image_detail_",
    )
)

if __name__ == "__main__":
    print("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
