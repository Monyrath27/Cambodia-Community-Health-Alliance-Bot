import os
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("TOKEN")

# Load CSV
data = pd.read_csv("diseases.csv")

# Convert to dictionary
responses = {}
for _, row in data.iterrows():
    responses[row["Keyword"].lower()] = {
        "EN": row["Reply_EN"],
        "KH": row["Reply_KH"],
    }

# Store user language preference
user_language = {}

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["🇬🇧 English", "🇰🇭 ខ្មែរ"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to Health Information Bot 🏥\nPlease choose your language:",
        reply_markup=reply_markup,
    )

# Handle messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.message.from_user.id

    # Language selection
    if "english" in text:
        user_language[user_id] = "EN"
        keyboard = [["📋 Disease List"], ["ℹ️ About"]]
        await update.message.reply_text(
            "Language set to English.",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )
        return

    if "ខ្មែរ" in text:
        user_language[user_id] = "KH"
        keyboard = [["📋 បញ្ជីជំងឺ"], ["ℹ️ អំពី"]]
        await update.message.reply_text(
            "បានកំណត់ភាសាខ្មែរ។",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )
        return

    # Disease search
    lang = user_language.get(user_id, "EN")

    for keyword in responses:
        if keyword in text:
            await update.message.reply_text(responses[keyword][lang])
            return

    # About
    if "about" in text or "អំពី" in text:
        if lang == "EN":
            await update.message.reply_text(
                "This NGO Health Bot provides basic disease information for educational purposes."
            )
        else:
            await update.message.reply_text(
                "បុត្រាអង្គការសុខភាពនេះផ្តល់ព័ត៌មានជំងឺសម្រាប់ការអប់រំ។"
            )
        return

    # Default reply
    if lang == "EN":
        await update.message.reply_text(
            "Please type a disease name (e.g., dengue, malaria)."
        )
    else:
        await update.message.reply_text(
            "សូមវាយបញ្ចូលឈ្មោះជំងឺ (ឧ. dengue, malaria)."
        )

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

app.run_polling()
