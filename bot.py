import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

TOKEN = "8496550115:AAG1VqdWMTU-t_oQ0etBzDkVFq5DJAZmEjY"

# Load CSV file
data = pd.read_csv("diseases.csv")

# Convert to dictionary
responses = {}
for index, row in data.iterrows():
    keyword = row["Keyword"].lower()
    reply = f"{row['Reply_EN']}\n\n{row['Reply_KH']}"
    responses[keyword] = reply

async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.lower()

    for keyword in responses:
        if keyword in user_message:
            await update.message.reply_text(responses[keyword])
            return

    await update.message.reply_text("Sorry, disease not found. Please try another keyword.")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

import os

PORT = int(os.environ.get("PORT", 10000))
app.run_polling()