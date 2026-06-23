# Telegram intermodal bot (group-ready)
# Live: Text -> Image, Image -> Text, Speech -> Text, Speech -> Image, Text -> Speech, Image -> Speech
# All follow-up buttons are keyed per-message, so they work correctly when multiple
# people interact with the bot in the same group chat.

import asyncio
import base64
import os
from io import BytesIO
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from google import genai
from google.genai import types
from huggingface_hub import InferenceClient

# --------------------------------------------------------------------------
# Environment / credentials
# --------------------------------------------------------------------------
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
HF_TOKEN = os.getenv("HF_TOKEN")

print("TELEGRAM_TOKEN found:", bool(TELEGRAM_TOKEN))
print("GEMINI_API_KEY found:", bool(GEMINI_API_KEY))
print("HF_TOKEN found:", bool(HF_TOKEN))

if not TELEGRAM_TOKEN:
    raise RuntimeError(f"TELEGRAM_TOKEN not found. Checked env file: {env_path}")
if not GEMINI_API_KEY:
    raise RuntimeError(f"GEMINI_API_KEY not found. Checked env file: {env_path}")
if not HF_TOKEN:
    raise RuntimeError(f"HF_TOKEN not found. Checked env file: {env_path}")

application = Application.builder().token(TELEGRAM_TOKEN).build()
client = genai.Client(api_key=GEMINI_API_KEY)
hf_client = InferenceClient(token=HF_TOKEN)

# Swap these for any other models you have access to on HF.
HF_IMAGE_MODEL = "black-forest-labs/FLUX.1-schnell"
HF_VISION_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"
HF_ASR_MODEL = "openai/whisper-large-v3-turbo"
HF_TTS_MODEL = "facebook/mms-tts"
GEMINI_TTS_MODEL = "gemini-3.1-flash-tts-preview"
GEMINI_TTS_VOICE = "Kore"

DEFAULT_INTERPRET_QUESTION = (
    "Give a concise one-paragraph summary of this image. "
    "Focus on the main objects, mood, and context."
)


# --------------------------------------------------------------------------
# Text -> Image (Gemini primary, Hugging Face fallback)
# --------------------------------------------------------------------------
def generate_image_gemini(prompt: str) -> Image.Image:
    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[prompt],
        config=types.GenerateContentConfig(response_modalities=["IMAGE"]),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return Image.open(BytesIO(part.inline_data.data))
    raise RuntimeError("Gemini response did not contain image data.")


def _translate_to_english(prompt: str) -> str:
    """
    Translate a prompt to English for the HF image generation fallback.

    Gemini handles non-English prompts natively. FLUX is trained primarily
    on English-captioned images and produces unreliable results with
    non-English text, so we translate silently before passing to HF.

    If the prompt is already English (or translation fails), the original
    is returned unchanged so generation can still proceed.
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=(
                "Translate the following image generation prompt to English. "
                "If it is already in English, return it unchanged. "
                "Return only the translated prompt, nothing else.\n\n"
                f"Prompt: {prompt}"
            ),
        )
        translated = response.text.strip()
        if translated and translated != prompt:
            print(f"Translated prompt for HF: '{prompt}' → '{translated}'")
        return translated or prompt
    except Exception as e:
        print(f"Translation failed ({e!r}); using original prompt for HF.")
        return prompt


def generate_image_hf(prompt: str, model: str = HF_IMAGE_MODEL) -> Image.Image:
    return hf_client.text_to_image(prompt, model=model)


def generate_image(prompt: str, hf_model: str = HF_IMAGE_MODEL) -> tuple[Image.Image, str]:
    try:
        return generate_image_gemini(prompt), "gemini"
    except Exception as gemini_error:
        print(f"Gemini (image gen) failed ({gemini_error!r}); falling back to Hugging Face.")

    try:
        english_prompt = _translate_to_english(prompt)
        return generate_image_hf(english_prompt, model=hf_model), "huggingface"
    except Exception as hf_error:
        raise RuntimeError("Both Gemini and Hugging Face image generation failed.") from hf_error


# --------------------------------------------------------------------------
# Image -> Text (Gemini primary, Hugging Face fallback)
# --------------------------------------------------------------------------
def interpret_image_gemini(image: Image.Image, question: str = DEFAULT_INTERPRET_QUESTION) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[question, image],
    )
    return response.text.strip()


def _image_to_data_uri(image: Image.Image) -> str:
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"


def interpret_image_hf(
    image: Image.Image,
    question: str = DEFAULT_INTERPRET_QUESTION,
    model: str = HF_VISION_MODEL,
) -> str:
    data_uri = _image_to_data_uri(image)
    completion = hf_client.chat_completion(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ],
    )
    return completion.choices[0].message.content.strip()


def interpret_image(
    image: Image.Image,
    question: str = DEFAULT_INTERPRET_QUESTION,
    hf_model: str = HF_VISION_MODEL,
) -> tuple[str, str]:
    try:
        return interpret_image_gemini(image, question), "gemini"
    except Exception as gemini_error:
        print(f"Gemini (interpret) failed ({gemini_error!r}); falling back to Hugging Face.")

    try:
        return interpret_image_hf(image, question, model=hf_model), "huggingface"
    except Exception as hf_error:
        raise RuntimeError("Both Gemini and Hugging Face image interpretation failed.") from hf_error


# --------------------------------------------------------------------------
# Speech -> Text (Gemini primary, Hugging Face Whisper fallback)
# --------------------------------------------------------------------------
_AUDIO_MIME_MAP = {
    "ogg": "audio/ogg", "oga": "audio/ogg", "mp3": "audio/mp3",
    "wav": "audio/wav", "m4a": "audio/mp4", "flac": "audio/flac",
}


def transcribe_audio_gemini(audio_path: Path) -> str:
    audio_bytes = Path(audio_path).read_bytes()
    suffix = Path(audio_path).suffix.lower().lstrip(".")
    mime_type = _AUDIO_MIME_MAP.get(suffix, "audio/ogg")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            "Transcribe this audio exactly, word for word. Return only the transcription.",
            types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
        ],
    )
    return response.text.strip()


def transcribe_audio_hf(audio_path: Path, model: str = HF_ASR_MODEL) -> str:
    output = hf_client.automatic_speech_recognition(str(audio_path), model=model)
    return output.text.strip()


def transcribe_audio(audio_path: Path, hf_model: str = HF_ASR_MODEL) -> tuple[str, str]:
    try:
        return transcribe_audio_gemini(audio_path), "gemini"
    except Exception as gemini_error:
        print(f"Gemini (transcribe) failed ({gemini_error!r}); falling back to Hugging Face.")

    try:
        return transcribe_audio_hf(audio_path, model=hf_model), "huggingface"
    except Exception as hf_error:
        raise RuntimeError("Both Gemini and Hugging Face transcription failed.") from hf_error


# --------------------------------------------------------------------------
# Text -> Speech (Gemini primary, Hugging Face fallback)
# --------------------------------------------------------------------------
def _pcm_to_wav_bytes(pcm_data: bytes, channels: int = 1, rate: int = 24000, sample_width: int = 2) -> bytes:
    """Gemini's TTS returns raw PCM; wrap it in a WAV header so any player can read it."""
    import wave

    buffer = BytesIO()
    with wave.open(buffer, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)
    return buffer.getvalue()


def synthesize_speech_gemini(text: str, voice: str = GEMINI_TTS_VOICE) -> bytes:
    response = client.models.generate_content(
        model=GEMINI_TTS_MODEL,
        contents=text,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voice)
                )
            ),
        ),
    )
    pcm_data = response.candidates[0].content.parts[0].inline_data.data
    return _pcm_to_wav_bytes(pcm_data)


def synthesize_speech_hf(text: str, model: str = HF_TTS_MODEL) -> bytes:
    return hf_client.text_to_speech(text, model=model)


def synthesize_speech(text: str, hf_model: str = HF_TTS_MODEL) -> tuple[bytes, str]:
    """
    Try Gemini first, fall back to Hugging Face if Gemini fails.
    Returns (wav_bytes, source) where source is "gemini" or "huggingface".
    """
    try:
        return synthesize_speech_gemini(text), "gemini"
    except Exception as gemini_error:
        print(f"Gemini (TTS) failed ({gemini_error!r}); falling back to Hugging Face.")

    try:
        return synthesize_speech_hf(text, model=hf_model), "huggingface"
    except Exception as hf_error:
        raise RuntimeError("Both Gemini and Hugging Face speech synthesis failed.") from hf_error


# --------------------------------------------------------------------------
# Prompt refinement (used by ✨ Refine & regenerate)
# --------------------------------------------------------------------------
REFINE_INSTRUCTION = (
    "You are an expert at writing prompts for AI image generation. "
    "Rewrite the following prompt to be visually specific, concrete, and entirely "
    "positive — avoid negations like 'not', 'without', 'no', 'don't'. "
    "Describe what should be visible, not what should be absent. "
    "Return only the rewritten prompt, nothing else."
)


def refine_prompt_gemini(prompt: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{REFINE_INSTRUCTION}\n\nOriginal prompt: {prompt}",
    )
    return response.text.strip()


def refine_prompt_hf(prompt: str) -> str:
    completion = hf_client.chat_completion(
        model=HF_VISION_MODEL,
        messages=[{"role": "user", "content": f"{REFINE_INSTRUCTION}\n\nOriginal prompt: {prompt}"}],
    )
    return completion.choices[0].message.content.strip()


def refine_prompt(prompt: str) -> tuple[str, str]:
    """Rewrite a prompt to be more AI-image-generation friendly. Returns (refined_prompt, source)."""
    try:
        return refine_prompt_gemini(prompt), "gemini"
    except Exception as gemini_error:
        print(f"Gemini (refine) failed ({gemini_error!r}); falling back to Hugging Face.")
    try:
        return refine_prompt_hf(prompt), "huggingface"
    except Exception as hf_error:
        raise RuntimeError("Both Gemini and Hugging Face prompt refinement failed.") from hf_error


# --------------------------------------------------------------------------
# Bot persona / orientation
# --------------------------------------------------------------------------
def _detect_language(update: Update) -> str:
    """
    Return a two-letter language code from the user's Telegram language setting.
    Supports de, fr, it; falls back to en for everything else.
    """
    code = (update.message.from_user.language_code or "en").lower()[:2]
    return code if code in ("de", "fr", "it") else "en"


_ATTRIBUTION = (
    "\u2014\n"
    "\u00a9 Anet Nyffeler\n"
    "chat\u2011room.ch \u2014 {tagline}\n"
    "{support}"
)

WELCOME_TEXTS = {
    "en": (
        "Hello! I'm your guide here \u2014 I help you create, describe, and build on "
        "text, images, and speech.\n\n"
        "Send me a photo, a voice message, or a text prompt. I'll help you generate "
        "images, describe what you see, transcribe what you hear, and speak written "
        "text aloud. You can also reply to another member's contribution and add your "
        "own layer to it.\n\n"
        "Type /help to see all the options.\n\n"
        + _ATTRIBUTION.format(
            tagline="an intermodal communication platform",
            support="With the kind support of Universit\u00e4t Bern and Zurich University of the Arts.",
        )
    ),
    "de": (
        "Hallo! Ich bin dein Guide \u2014 ich helfe dir, Texte, Bilder und Sprache zu "
        "erstellen, zu beschreiben und weiterzuentwickeln.\n\n"
        "Schick mir ein Foto, eine Sprachnachricht oder einen Textprompt. Ich helfe dir, "
        "Bilder zu generieren, zu beschreiben was du siehst, zu transkribieren was du "
        "h\u00f6rst, und Texte laut vorzulesen. Du kannst auch auf den Beitrag eines "
        "anderen Mitglieds antworten und eine eigene Ebene hinzuf\u00fcgen.\n\n"
        "Tippe /help f\u00fcr alle Optionen.\n\n"
        + _ATTRIBUTION.format(
            tagline="eine intermodale Kommunikationsplattform",
            support="Mit freundlicher Unterst\u00fctzung der Universit\u00e4t Bern und der Z\u00fcrcher Hochschule der K\u00fcnste.",
        )
    ),
    "fr": (
        "Bonjour\u00a0! Je suis ton guide \u2014 je t\u2019aide \u00e0 cr\u00e9er, "
        "d\u00e9crire et enrichir textes, images et parole.\n\n"
        "Envoie-moi une photo, un message vocal ou un prompt textuel. Je t\u2019aiderai "
        "\u00e0 g\u00e9n\u00e9rer des images, d\u00e9crire ce que tu vois, transcrire ce "
        "que tu entends, et lire des textes \u00e0 voix haute. Tu peux aussi r\u00e9pondre "
        "\u00e0 la contribution d\u2019un autre membre et y ajouter ta propre couche.\n\n"
        "Tape /help pour voir toutes les options.\n\n"
        + _ATTRIBUTION.format(
            tagline="une plateforme de communication intermodale",
            support="Avec le soutien bienveillant de l\u2019Universit\u00e9 de Berne et de la Haute \u00e9cole des arts de Zurich.",
        )
    ),
    "it": (
        "Ciao! Sono la tua guida \u2014 ti aiuto a creare, descrivere e sviluppare "
        "testi, immagini e voci.\n\n"
        "Inviami una foto, un messaggio vocale o un prompt testuale. Ti aiuter\u00f2 a "
        "generare immagini, descrivere ci\u00f2 che vedi, trascrivere ci\u00f2 che senti "
        "e leggere testi ad alta voce. Puoi anche rispondere al contributo di un altro "
        "membro e aggiungere il tuo livello.\n\n"
        "Digita /help per vedere tutte le opzioni.\n\n"
        + _ATTRIBUTION.format(
            tagline="una piattaforma di comunicazione intermodale",
            support="Con il gentile supporto dell\u2019Universit\u00e0 di Berna e della Scuola universitaria delle arti di Zurigo.",
        )
    ),
}

HELP_TEXTS = {
    "en": (
        "Here are the paths you can choose:\n\n"
        "\u2705 Image \u2192 Text \u2014 send me a photo and I\u2019ll describe it\n"
        "\u2705 Text \u2192 Image \u2014 /image <description>\n"
        "\u2705 Speech \u2192 Text \u2014 send me a voice message and I\u2019ll transcribe it\n"
        "\u2705 Speech \u2192 Image \u2014 send a voice message, then tap \u201cGenerate image from this\u201d\n"
        "\u2705 Text \u2192 Speech \u2014 /speak <text>\n"
        "\u2705 Image \u2192 Speech \u2014 send a photo, then tap \u201cRead this aloud\u201d\n\n"
        "Reply to any photo or generated image with /image and a new instruction "
        "to build on it \u2014 the bot combines the original image with your idea:\n"
        "Example: reply to a photo \u2192 /image turn the hair red\n\n"
        "Under generated images you\u2019ll find two refinement options:\n"
        "\u2728 Auto-refine \u2014 the bot rewrites your prompt to be clearer and more AI-friendly\n"
        "\u270f\ufe0f Edit prompt \u2014 type your own version (you can add negative terms, "
        "e.g. negative: yellow, cars)\n\n"
        "Example: /image a woman horseback riding through green hills at sunrise\n"
        "Example: /speak Good morning, how are you today?\n\n"
        "You can send prompts in any language. For best image generation results, "
        "English prompts work most reliably."
    ),
    "de": (
        "Hier sind deine M\u00f6glichkeiten:\n\n"
        "\u2705 Bild \u2192 Text \u2014 schick mir ein Foto und ich beschreibe es\n"
        "\u2705 Text \u2192 Bild \u2014 /image <Beschreibung>\n"
        "\u2705 Sprache \u2192 Text \u2014 schick mir eine Sprachnachricht und ich transkribiere sie\n"
        "\u2705 Sprache \u2192 Bild \u2014 Sprachnachricht senden, dann \u201eBild daraus generieren\u201c tippen\n"
        "\u2705 Text \u2192 Sprache \u2014 /speak <Text>\n"
        "\u2705 Bild \u2192 Sprache \u2014 Foto senden, dann \u201eLaut vorlesen\u201c tippen\n\n"
        "Antworte auf ein Foto oder generiertes Bild mit /image und einer neuen Anweisung, "
        "um darauf aufzubauen \u2014 der Bot kombiniert das Originalbild mit deiner Idee:\n"
        "Beispiel: auf ein Foto antworten \u2192 /image die Haare rot f\u00e4rben\n\n"
        "Unter generierten Bildern findest du zwei Verfeinerungsoptionen:\n"
        "\u2728 Auto-verfeinern \u2014 der Bot schreibt deinen Prompt klarer und KI-freundlicher um\n"
        "\u270f\ufe0f Prompt bearbeiten \u2014 schreib deine eigene Version (du kannst negative Begriffe "
        "hinzuf\u00fcgen, z.\u202fB. negativ: gelb, Autos)\n\n"
        "Beispiel: /image eine Frau reitet durch gr\u00fcne H\u00fcgel bei Sonnenaufgang\n"
        "Beispiel: /speak Guten Morgen, wie geht es dir?\n\n"
        "Du kannst Prompts in jeder Sprache eingeben. F\u00fcr beste Ergebnisse bei der "
        "Bildgenerierung funktionieren englische Prompts am zuverl\u00e4ssigsten."
    ),
    "fr": (
        "Voici tes options\u00a0:\n\n"
        "\u2705 Image \u2192 Texte \u2014 envoie-moi une photo et je la d\u00e9crirai\n"
        "\u2705 Texte \u2192 Image \u2014 /image <description>\n"
        "\u2705 Parole \u2192 Texte \u2014 envoie un message vocal et je le transcrirai\n"
        "\u2705 Parole \u2192 Image \u2014 envoie un message vocal, puis tape \u00ab\u202fG\u00e9n\u00e9rer une image\u202f\u00bb\n"
        "\u2705 Texte \u2192 Parole \u2014 /speak <texte>\n"
        "\u2705 Image \u2192 Parole \u2014 envoie une photo, puis tape \u00ab\u202fLire \u00e0 voix haute\u202f\u00bb\n\n"
        "R\u00e9ponds \u00e0 n\u2019importe quelle photo ou image g\u00e9n\u00e9r\u00e9e "
        "avec /image et une nouvelle instruction pour y ajouter ta couche\u00a0:\n"
        "Exemple\u00a0: r\u00e9pondre \u00e0 une photo \u2192 /image changer les cheveux en rouge\n\n"
        "Sous les images g\u00e9n\u00e9r\u00e9es, tu trouveras deux options de raffinement\u00a0:\n"
        "\u2728 Affiner automatiquement \u2014 le bot r\u00e9\u00e9crit ton prompt pour le rendre plus clair\n"
        "\u270f\ufe0f Modifier le prompt \u2014 \u00e9cris ta propre version (tu peux ajouter des termes "
        "n\u00e9gatifs, p.\u202fex. n\u00e9gatif\u00a0: jaune, voitures)\n\n"
        "Exemple\u00a0: /image une femme \u00e0 cheval dans des collines verdoyantes au lever du soleil\n"
        "Exemple\u00a0: /speak Bonjour, comment vas-tu\u00a0?\n\n"
        "Tu peux envoyer des prompts dans n\u2019importe quelle langue. Pour de meilleurs "
        "r\u00e9sultats, les prompts en anglais fonctionnent le plus fiablement."
    ),
    "it": (
        "Ecco le tue opzioni:\n\n"
        "\u2705 Immagine \u2192 Testo \u2014 inviami una foto e la descriver\u00f2\n"
        "\u2705 Testo \u2192 Immagine \u2014 /image <descrizione>\n"
        "\u2705 Voce \u2192 Testo \u2014 inviami un messaggio vocale e lo trascrivo\n"
        "\u2705 Voce \u2192 Immagine \u2014 invia un messaggio vocale, poi tocca \u00abGenera immagine\u00bb\n"
        "\u2705 Testo \u2192 Voce \u2014 /speak <testo>\n"
        "\u2705 Immagine \u2192 Voce \u2014 invia una foto, poi tocca \u00abLeggi ad alta voce\u00bb\n\n"
        "Rispondi a qualsiasi foto o immagine generata con /image e una nuova istruzione "
        "per costruire su di essa \u2014 il bot combina l\u2019immagine originale con la tua idea:\n"
        "Esempio: rispondi a una foto \u2192 /image rendi i capelli rossi\n\n"
        "Sotto le immagini generate troverai due opzioni di rifinitura:\n"
        "\u2728 Affina automaticamente \u2014 il bot riscrive il tuo prompt per renderlo pi\u00f9 chiaro\n"
        "\u270f\ufe0f Modifica prompt \u2014 scrivi la tua versione (puoi aggiungere termini negativi, "
        "es. negativo: giallo, macchine)\n\n"
        "Esempio: /image una donna a cavallo tra colline verdi all\u2019alba\n"
        "Esempio: /speak Buongiorno, come stai?\n\n"
        "Puoi inviare prompt in qualsiasi lingua. Per i migliori risultati nella "
        "generazione di immagini, i prompt in inglese funzionano nel modo pi\u00f9 affidabile."
    ),
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _detect_language(update)
    await update.message.reply_text(WELCOME_TEXTS[lang])


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = _detect_language(update)
    await update.message.reply_text(HELP_TEXTS[lang])


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    pending_key = _pending_edit_key(user_id)
    if pending_key in context.chat_data:
        del context.chat_data[pending_key]
        await update.message.reply_text("Prompt editing cancelled.")
    else:
        await update.message.reply_text("Nothing to cancel.")


application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("cancel", cancel_command))


# --------------------------------------------------------------------------
# /image command: Text -> Image, with optional reply-to-photo context
# --------------------------------------------------------------------------
async def image_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args).strip() if context.args else ""
    author = update.message.from_user.first_name

    if not prompt:
        await update.message.reply_text(
            "Please include a description, e.g.\n"
            "/image a woman horseback riding through green hills at sunrise\n\n"
            "You can also reply to any photo with /image and an instruction:\n"
            "/image turn the hair red"
        )
        return

    # Check if this /image command is a reply to a message containing a photo,
    # OR a reply to the bot's text summary of a previously uploaded photo.
    reply_msg = update.message.reply_to_message
    referenced_image_description = None
    ref_temp_path = None

    if reply_msg:
        ref_file_id = None

        if reply_msg.photo:
            # Direct reply to a photo message (bot-generated or user-uploaded)
            ref_file_id = reply_msg.photo[-1].file_id

        else:
            # Reply to a text message — check if it's a bot summary with a stored photo
            stored_file_id = context.chat_data.get(_image_file_id_key(reply_msg.message_id), "")
            if stored_file_id:
                ref_file_id = stored_file_id

        if ref_file_id:
            await update.message.reply_text(
                f"Reading the referenced photo and combining it with {author}'s instruction..."
            )
            ref_file = await context.bot.get_file(ref_file_id)
            ref_temp_path = SCRIPT_DIR / f"temp_ref_{ref_file_id}.jpg"
            try:
                await ref_file.download_to_drive(custom_path=ref_temp_path)
                with Image.open(ref_temp_path) as ref_image:
                    ref_image.load()
                    ref_description, _ = await asyncio.to_thread(interpret_image, ref_image)
                referenced_image_description = ref_description
            except Exception as e:
                await update.message.reply_text(
                    f"Could not read the referenced photo ({e}). Generating from text prompt only."
                )
            finally:
                if ref_temp_path and ref_temp_path.exists():
                    ref_temp_path.unlink()

    # Build the final generation prompt
    if referenced_image_description:
        final_prompt = (
            f"Starting from this scene: {referenced_image_description}\n\n"
            f"Now apply this change: {prompt}"
        )
    else:
        final_prompt = prompt

    await update.message.reply_text(f"Generating {author}'s image...")

    try:
        image, source = await asyncio.to_thread(generate_image, final_prompt)
    except Exception as e:
        await update.message.reply_text(f"Image generation failed: {e}")
        return

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "generated_image.png"

    backend = "Gemini" if source == "gemini" else "Hugging Face (fallback)"
    caption = (
        f"Generated by {author} via {backend}\n"
        f"Prompt: {prompt[:200]}"
    )
    sent_message = await update.message.reply_photo(
        photo=buffer,
        caption=caption,
        reply_markup=_generated_image_keyboard(),
    )

    # Store the prompt and author for the ✨ Refine & regenerate button
    context.chat_data[_image_prompt_key(sent_message.message_id)] = final_prompt
    context.chat_data[_content_author_key(sent_message.message_id)] = author


application.add_handler(CommandHandler("image", image_command))


# --------------------------------------------------------------------------
# /speak command: Text -> Speech
# --------------------------------------------------------------------------
async def speak_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args).strip() if context.args else ""

    if not text:
        await update.message.reply_text(
            "Please include the text to speak, e.g.\n/speak Good morning, how are you today?"
        )
        return

    await update.message.reply_text("Synthesizing speech...")

    try:
        audio_bytes, source = await asyncio.to_thread(synthesize_speech, text)
    except Exception as e:
        await update.message.reply_text(f"Speech synthesis failed: {e}")
        return

    buffer = BytesIO(audio_bytes)
    buffer.name = "speech.wav"

    caption = "Generated via Gemini" if source == "gemini" else "Generated via Hugging Face (fallback)"
    await update.message.reply_audio(audio=buffer, caption=caption)


application.add_handler(CommandHandler("speak", speak_command))


# --------------------------------------------------------------------------
# Photo handler: Image -> Text
# --------------------------------------------------------------------------
def _follow_up_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Main Objects", callback_data="image_detail_main")],
            [InlineKeyboardButton("Mood", callback_data="image_detail_mood")],
            [InlineKeyboardButton("Context", callback_data="image_detail_context")],
            [InlineKeyboardButton("\U0001F50A Read this aloud", callback_data="image_to_speech")],
        ]
    )


def _image_summary_key(message_id: int) -> str:
    """
    Per-message key for storing an image summary in chat_data.

    Keying by the bot's own reply message_id (the one carrying the follow-up
    buttons) ties the data to the specific photo it came from, not to
    whoever happens to tap the button. This means anyone in a group can use
    the follow-up buttons on anyone else's photo correctly, instead of only
    the original sender being able to use their own buttons.
    """
    return f"image_summary:{message_id}"


def _image_prompt_key(message_id: int) -> str:
    """Per-message key for storing the original prompt used to generate an image."""
    return f"image_prompt:{message_id}"


def _image_file_id_key(message_id: int) -> str:
    """Per-message key for storing the Telegram file_id of the original uploaded photo.
    Allows /image to retrieve the photo when the user replies to the bot's text summary
    rather than to the photo itself."""
    return f"image_file_id:{message_id}"


def _content_author_key(message_id: int) -> str:
    """Per-message key for storing the first name of whoever triggered this content."""
    return f"content_author:{message_id}"


def _generated_image_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for bot-generated images: auto-refine or manual prompt editing."""
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("\u2728 Auto-refine", callback_data="auto_refine_image")],
            [InlineKeyboardButton("\u270f\ufe0f Edit prompt", callback_data="edit_prompt_image")],
        ]
    )


def _pending_edit_key(user_id: int) -> str:
    """Per-user key flagging that this user is currently typing a refined prompt."""
    return f"pending_edit:{user_id}"


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.photo:
        return

    author = update.message.from_user.first_name
    await update.message.reply_text(f"Analyzing {author}'s image...")

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    temp_path = SCRIPT_DIR / f"temp_{photo.file_id}.jpg"

    try:
        await file.download_to_drive(custom_path=temp_path)
        with Image.open(temp_path) as image:
            image.load()
            summary, source = await asyncio.to_thread(interpret_image, image)

        caption_note = "" if source == "gemini" else " (via Hugging Face fallback)"
        sent_message = await update.message.reply_text(
            f"{author}'s image{caption_note}:\n\n{summary[:3800]}"
            f"\n\nWhich aspect would you like to explore further?",
            reply_markup=_follow_up_keyboard(),
        )
        context.chat_data[_image_summary_key(sent_message.message_id)] = summary
        context.chat_data[_image_file_id_key(sent_message.message_id)] = photo.file_id
        context.chat_data[_content_author_key(sent_message.message_id)] = author
    except Exception as e:
        await update.message.reply_text(f"Image analysis failed: {e}")
    finally:
        if temp_path.exists():
            temp_path.unlink()


application.add_handler(MessageHandler(filters.PHOTO, handle_photo))


# --------------------------------------------------------------------------
# Voice/audio handler: Speech -> Text, with a follow-up for Speech -> Image
# --------------------------------------------------------------------------
def _transcript_key(message_id: int) -> str:
    """Per-message key for storing a transcript, same reasoning as _image_summary_key."""
    return f"transcript:{message_id}"


def _transcript_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("\U0001F3A8 Generate image from this", callback_data="speech_to_image")]]
    )


async def handle_voice_or_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice_or_audio = update.message.voice or update.message.audio
    if voice_or_audio is None:
        return

    await update.message.reply_text("Transcribing your voice message...")

    file = await context.bot.get_file(voice_or_audio.file_id)
    # Voice messages are .oga (Ogg/Opus); uploaded audio files may carry their own name.
    suffix = Path(getattr(voice_or_audio, "file_name", "") or "").suffix or ".oga"
    temp_path = SCRIPT_DIR / f"temp_{voice_or_audio.file_unique_id}{suffix}"

    try:
        await file.download_to_drive(custom_path=temp_path)
        transcript, source = await asyncio.to_thread(transcribe_audio, temp_path)

        source_note = "" if source == "gemini" else " (via Hugging Face fallback)"
        sent_message = await update.message.reply_text(
            f"Transcript{source_note}:\n\n{transcript}",
            reply_markup=_transcript_keyboard(),
        )
        context.chat_data[_transcript_key(sent_message.message_id)] = transcript
    except Exception as e:
        await update.message.reply_text(f"Transcription failed: {e}")
    finally:
        if temp_path.exists():
            temp_path.unlink()


application.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice_or_audio))


async def handle_speech_to_image_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    transcript = context.chat_data.get(_transcript_key(query.message.message_id), "")
    if not transcript:
        await query.edit_message_text("No transcript is available yet. Please send a new voice message.")
        return

    await query.message.reply_text("Generating your image...")

    try:
        image, source = await asyncio.to_thread(generate_image, transcript)
    except Exception as e:
        await query.message.reply_text(f"Image generation failed: {e}")
        return

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "generated_image.png"

    caption = "Generated via Gemini" if source == "gemini" else "Generated via Hugging Face (fallback)"
    await query.message.reply_photo(photo=buffer, caption=caption)


application.add_handler(CallbackQueryHandler(handle_speech_to_image_callback, pattern="^speech_to_image$"))


async def handle_image_to_speech_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    summary = context.chat_data.get(_image_summary_key(query.message.message_id), "")
    if not summary:
        await query.edit_message_text("No image summary is available yet. Please send a new image.")
        return

    await query.message.reply_text("Synthesizing speech...")

    try:
        audio_bytes, source = await asyncio.to_thread(synthesize_speech, summary)
    except Exception as e:
        await query.message.reply_text(f"Speech synthesis failed: {e}")
        return

    buffer = BytesIO(audio_bytes)
    buffer.name = "speech.wav"

    caption = "Generated via Gemini" if source == "gemini" else "Generated via Hugging Face (fallback)"
    await query.message.reply_audio(audio=buffer, caption=caption)


application.add_handler(CallbackQueryHandler(handle_image_to_speech_callback, pattern="^image_to_speech$"))


# --------------------------------------------------------------------------
# ✨ Refine & regenerate callback
# --------------------------------------------------------------------------
async def handle_auto_refine_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """✨ Auto-refine: AI rewrites the prompt to be clearer and more image-generation friendly."""
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    original_prompt = context.chat_data.get(_image_prompt_key(query.message.message_id), "")
    original_author = context.chat_data.get(_content_author_key(query.message.message_id), "someone")

    if not original_prompt:
        await query.message.reply_text(
            "No prompt is stored for this image. Please generate a new image with /image."
        )
        return

    refiner = query.from_user.first_name
    await query.message.reply_text(
        f"{refiner} is auto-refining {original_author}'s prompt...\n\n"
        f"Original: \"{original_prompt[:300]}\""
    )

    try:
        refined_prompt, refine_source = await asyncio.to_thread(refine_prompt, original_prompt)
    except Exception as e:
        await query.message.reply_text(f"Prompt refinement failed: {e}")
        return

    await query.message.reply_text(
        f"Refined ({refine_source}): \"{refined_prompt[:300]}\"\n\nGenerating..."
    )

    try:
        image, gen_source = await asyncio.to_thread(generate_image, refined_prompt)
    except Exception as e:
        await query.message.reply_text(f"Image generation failed: {e}")
        return

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    buffer.name = "generated_image.png"

    backend = "Gemini" if gen_source == "gemini" else "Hugging Face (fallback)"
    caption = (
        f"Auto-refined by {refiner} from {original_author}'s prompt, via {backend}\n"
        f"Prompt: {refined_prompt[:200]}"
    )
    sent_message = await query.message.reply_photo(
        photo=buffer,
        caption=caption,
        reply_markup=_generated_image_keyboard(),
    )
    context.chat_data[_image_prompt_key(sent_message.message_id)] = refined_prompt
    context.chat_data[_content_author_key(sent_message.message_id)] = refiner


application.add_handler(CallbackQueryHandler(handle_auto_refine_callback, pattern="^auto_refine_image$"))


async def handle_edit_prompt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """✏️ Edit prompt: ask the user to type their own refined prompt."""
    query = update.callback_query
    if query is None:
        return

    await query.answer()

    original_prompt = context.chat_data.get(_image_prompt_key(query.message.message_id), "")
    original_author = context.chat_data.get(_content_author_key(query.message.message_id), "someone")

    if not original_prompt:
        await query.message.reply_text(
            "No prompt is stored for this image. Please generate a new image with /image."
        )
        return

    editor = query.from_user.first_name

    # Store pending edit state for this user, referencing the original author
    context.chat_data[_pending_edit_key(query.from_user.id)] = {
        "original_author": original_author,
    }

    await query.message.reply_text(
        f"{editor}, here is the current prompt:\n\n\"{original_prompt[:400]}\"\n\n"
        f"Type your refined version now. You can add negative terms, e.g.:\n"
        f"a person in a yellow jacket, negative: red\n\n"
        f"Send /cancel to abort."
    )


application.add_handler(CallbackQueryHandler(handle_edit_prompt_callback, pattern="^edit_prompt_image$"))


# --------------------------------------------------------------------------
# Follow-up detail buttons (text-based, using the stored summary)
# --------------------------------------------------------------------------
def ask_text_gemini(prompt: str) -> str:
    response = client.models.generate_content(model="gemini-2.5-flash", contents=[prompt])
    return response.text.strip()


def ask_text_hf(prompt: str, model: str = HF_VISION_MODEL) -> str:
    completion = hf_client.chat_completion(
        model=model,
        messages=[{"role": "user", "content": prompt}],
    )
    return completion.choices[0].message.content.strip()


def ask_text(prompt: str) -> tuple[str, str]:
    try:
        return ask_text_gemini(prompt), "gemini"
    except Exception as gemini_error:
        print(f"Gemini (text) failed ({gemini_error!r}); falling back to Hugging Face.")

    try:
        return ask_text_hf(prompt), "huggingface"
    except Exception as hf_error:
        raise RuntimeError("Both Gemini and Hugging Face text generation failed.") from hf_error


async def handle_image_detail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None:
        return

    await query.answer()
    choice = query.data or ""

    summary_key = _image_summary_key(query.message.message_id)
    summary = context.chat_data.get(summary_key, "")
    if not summary:
        await query.edit_message_text("No image summary is available yet. Please send a new image.")
        return

    prompts = {
        "image_detail_main": "Give me more information about the main objects in the image.",
        "image_detail_mood": "Explain the mood and atmosphere of the image in more detail.",
        "image_detail_context": "Explain the context and possible meaning of the image.",
    }
    question = prompts.get(choice, "Give me a bit more detail about this image.")

    await query.message.reply_text("Checking that detail now...")

    try:
        reply, source = await asyncio.to_thread(
            ask_text, f"Based on this image summary:\n{summary}\n\n{question}"
        )
        await query.message.reply_text(reply[:4000])
        followup_message = await query.message.reply_text(
            "Would you like more detail about another aspect?",
            reply_markup=_follow_up_keyboard(),
        )
        context.chat_data[_image_summary_key(followup_message.message_id)] = summary
    except Exception as e:
        await query.message.reply_text(f"Detail request failed: {e}")


application.add_handler(CallbackQueryHandler(handle_image_detail_callback, pattern="^image_detail_"))


# --------------------------------------------------------------------------
# Fallback for plain text: guide message, no chat Q&A
# --------------------------------------------------------------------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    pending_key = _pending_edit_key(user_id)
    pending = context.chat_data.get(pending_key)

    if pending:
        # This user tapped ✏️ Edit prompt and is now sending their refined version.
        del context.chat_data[pending_key]
        new_prompt = update.message.text.strip()
        editor = update.message.from_user.first_name
        original_author = pending.get("original_author", "someone")

        await update.message.reply_text(f"Generating with {editor}'s prompt...")

        try:
            image, gen_source = await asyncio.to_thread(generate_image, new_prompt)
        except Exception as e:
            await update.message.reply_text(f"Image generation failed: {e}")
            return

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        buffer.name = "generated_image.png"

        backend = "Gemini" if gen_source == "gemini" else "Hugging Face (fallback)"
        caption = (
            f"Edited by {editor} from {original_author}'s prompt, via {backend}\n"
            f"Prompt: {new_prompt[:200]}"
        )
        sent_message = await update.message.reply_photo(
            photo=buffer,
            caption=caption,
            reply_markup=_generated_image_keyboard(),
        )
        context.chat_data[_image_prompt_key(sent_message.message_id)] = new_prompt
        context.chat_data[_content_author_key(sent_message.message_id)] = editor
        return

    # No pending edit — standard guide message
    await update.message.reply_text(
        "I am your guide and here are the paths you can choose \u2014 just type /help to find out."
    )


application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


# --------------------------------------------------------------------------
# Fallback for unrecognized commands (e.g. typos like /speech instead of /speak)
# --------------------------------------------------------------------------
async def handle_unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"I don't recognize \"{update.message.text}\" as a command. Type /help to see what I can do."
    )


application.add_handler(MessageHandler(filters.COMMAND, handle_unknown_command))


if __name__ == "__main__":
    print("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)
