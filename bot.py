import os
import pandas as pd
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# 🟢 Get bot token from environment variable
TOKEN = os.environ.get("8496550115:AAG1VqdWMTU-t_oQ0etBzDkVFq5DJAZmEjY")
if TOKEN is None:
    raise ValueError("Bot token is missing! Add it as an environment variable.")

# 🟢 Load CSV
data = pd.read_csv("diseases.csv")

# 🟢 Prepare responses dictionary
responses = {}
for _, row in data.iterrows():
    responses[row["Keyword"].lower()] = {
        "EN": {
            "info": row["Reply_EN"],
            "symptoms": row.get("Symptoms_EN", ""),
            "prevention": row.get("Prevention_EN", "")
        },
        "KH": {
            "info": row["Reply_KH"],
            "symptoms": row.get("Symptoms_KH", ""),
            "prevention": row.get("Prevention_KH", "")
        }
    }

# 🟢 Prepare disease buttons
disease_buttons_EN = [[KeyboardButton(keyword)] for keyword in data['Keyword']]
if 'Keyword_KH' in data.columns:
    disease_buttons_KH = [[KeyboardButton(keyword)] for keyword in data['Keyword_KH']]
else:
    # If no Khmer keyword, reuse English for buttons
    disease_buttons_KH = disease_buttons_EN

# 🟢 Store user language
user_language = {}

# 🟢 /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("🇬🇧 English"), KeyboardButton("🇰🇭 ខ្មែរ")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome to Health Information Bot 🏥\nPlease choose your language / សូមជ្រើសរើសភាសា:",
        reply_markup=reply_markup,
    )

# 🟢 Handle messages
async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user_id = update.message.from_user.id

    # --- Language selection ---
    if "english" in text:
        user_language[user_id] = "EN"
        # Split buttons 3 per row
        keyboard = [disease_buttons_EN[i:i+3] for i in range(0, len(disease_buttons_EN), 3)]
        keyboard.append([KeyboardButton("ℹ️ About")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("Language set to English. Choose a disease:", reply_markup=reply_markup)
        return

    if "ខ្មែរ" in text:
        user_language[user_id] = "KH"
        keyboard = [disease_buttons_KH[i:i+3] for i in range(0, len(disease_buttons_KH), 3)]
        keyboard.append([KeyboardButton("ℹ️ អំពី")])
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("បានកំណត់ភាសាខ្មែរ។ សូមជ្រើសរើសជំងឺ:", reply_markup=reply_markup)
        return

    # --- Determine language ---
    lang = user_language.get(user_id, "EN")

    # --- About section ---
    if "about" in text or "អំពី" in text:
        if lang == "EN":
            await update.message.reply_text(
                "This NGO Health Bot provides educational info about common diseases, symptoms, and prevention."
            )
        else:
            await update.message.reply_text(
                "បុត្រាអង្គការសុខភាពនេះផ្តល់ព័ត៌មានអប់រំអំពីជំងឺ, លក្ខណៈរោគ, និងការពារ។"
            )
        return

    # --- Disease search ---
    for keyword in responses:
        if keyword in text:
            disease = responses[keyword][lang]
            reply_text = f"💉 {disease['info']}\n\n🩺 Symptoms: {disease['symptoms']}\n🛡️ Prevention: {disease['prevention']}"
            await update.message.reply_text(reply_text)
            return

    # --- Default reply ---
    if lang == "EN":
        await update.message.reply_text("Please type or click a disease name from the menu.")
    else:
        await update.message.reply_text("សូមវាយ ឬ ចុច ឈ្មោះជំងឺពីម៉ឺនុយ។")

# 🟢 Build app
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

# 🟢 Run bot
app.run_polling()
