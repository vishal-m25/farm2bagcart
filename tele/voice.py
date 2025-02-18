import logging
import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import vertexai
from vertexai.preview.generative_models import GenerativeModel, SafetySetting, Tool
from vertexai.preview.generative_models import grounding
from telegram.constants import ParseMode  
import speech_recognition as sr


# Initialize Vertex AI Chatbot
def initialize_vertex_ai(project_id, datastore):
    vertexai.init(project=project_id, location="us-central1")
    tools = [
        Tool.from_retrieval(
            retrieval=grounding.Retrieval(
                source=grounding.VertexAISearch(datastore=datastore),
            )
        )
    ]
    model = GenerativeModel(
        "gemini-1.0-pro-002",
        tools=tools,
    )
    return model.start_chat()

# Configuration for generation and safety
generation_config = {
    "max_output_tokens": 4500,
    "temperature": 1,
    "top_p": 1,
}

safety_settings = [
    SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
    SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_MEDIUM_AND_ABOVE"),
]


pre_prompt = """## Prompt for (Farm2Bag Human Assistant)

You are Farm2Bag's human assistant, and you **must only** answer using the provided Farm2Bag data.  
You **cannot** access, refer to, or generate responses from any external websites, news sources, or general knowledge.  

### **Strict Response Guidelines:**
1. **Farm2Bag-Only Responses:** If a question is unrelated to Farm2Bag's products, services, or operations, respond with:  
   ❌ **"Sorry, that's not available."**  
   ✅ Do **not** provide answers from outside sources.  
2. **Short and Precise Answers:** Responses must **not exceed 150 words.** Use concise language with relevant data.  
3. **Conversational & Friendly Tone:** Maintain a human-like, engaging style. Avoid overly technical jargon unless requested.  
4. **Language Matching:** Respond in the **same language** as the user's query.  
5. **Table Formatting (if applicable):** Use markdown tables for structured data.  
6. **No Guessing:** If the information is unavailable, **do not** make assumptions—simply state, **"Sorry, that's not available."**  

### **Example Interactions:**  

**User:** *What vegetables do you sell?*  
**Farm2Bag Assistant:**  
✅ "We offer fresh farm vegetables! Here’s a list:  

| Vegetable | Availability | Price (per kg) |  
|-----------|--------------|----------------|  
| Tomatoes  | Seasonal     | ₹40            |  
| Spinach   | Year-round   | ₹25            |  
| Carrots   | Seasonal     | ₹30            |  
| Onions    | Year-round   | ₹20            |  

🥬 Check our full list at www.farm2bag.com!"  

---  

**User:** *What’s the stock price of Google?*  
**Farm2Bag Assistant:** ❌ "Sorry, that's not available."  

**User:** *Tell me about the history of agriculture.*  
**Farm2Bag Assistant:** ❌ "Sorry, that's not available."  

**User:** *Where are you located?*  
**Farm2Bag Assistant:** ✅ "📍 **Office Location:** Farm2Bag, 5/396, Rajeev Gandhi Salai, OMR Thoraipakkam, Chennai - 600097, Tamil Nadu.  

📞 **Call Us:** +91 95000 37221 | +91 91761 85709 (Mon-Sat, 6 AM - 11 PM)  
📧 **Email:** farm2bag@gmail.com"  

---

### **Mandatory Instructions:**
✔ **Strictly adhere** to these guidelines.  
✔ **Never** generate responses from __external or own__ sources.  
✔ **Always** prioritize clarity, accuracy, and brevity.  
✔ If a question cannot be answered using Farm2Bag data, **respond only with**:  
   ❌ "Sorry, that's not available."  


"""

# Initialize chat session
project_id = "hardy-mercury-449710-f9"
datastore = "projects/hardy-mercury-449710-f9/locations/global/collections/default_collection/dataStores/farm-store_1738555123738"
chat_session = initialize_vertex_ai(project_id, datastore)

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7927080939:AAH13OQKQ5VVzcfetEfm8jLt5tjShC3YY_o"

# Speech-to-Text Function (Using Whisper API)
def convert_speech_to_text(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)  # Replace with Whisper API if needed
        except sr.UnknownValueError:
            return "Sorry, could not understand the audio."
        except sr.RequestError:
            return "Error: Could not request results from the speech recognition service."

# Telegram Bot Handlers
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hi! Welcome to Farm2Bag. How can I help you today?")

async def handle_text(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.strip()
    if not user_input:
        return
    try:
        # Get response from Vertex AI
        response = chat_session.send_message(
            [pre_prompt + user_input],
            generation_config=generation_config,
            safety_settings=safety_settings,
        ).text
        print(response)
        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def handle_voice(update: Update, context: CallbackContext) -> None:
    """Handles voice messages, converts them to text, and sends them to Vertex AI."""
    voice = update.message.voice
    if not voice:
        return

    file = await context.bot.get_file(voice.file_id)
    file_path = f"voice_messages/{voice.file_id}.ogg"

    # Ensure directory exists
    os.makedirs("voice_messages", exist_ok=True)

    # Download the voice message
    await file.download_to_drive(file_path)

    # Convert OGG to WAV using FFmpeg
    wav_path = file_path.replace(".ogg", ".wav")
    try:
        ffmpeg.input(file_path).output(wav_path, format="wav").run(overwrite_output=True)

        # Transcribe using Whisper
        text = transcribe_audio(wav_path)
        print(f"Transcribed Text: {text}")

        # Get AI response from Vertex AI
        response = chat_session.send_message(
            [pre_prompt + text],
            generation_config=generation_config,
            safety_settings=safety_settings,
        ).text
        print(response)

        await update.message.reply_text(response)

    except Exception as e:
        await update.message.reply_text(f"Error processing voice message: {str(e)}")

    finally:
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(wav_path):
            os.remove(wav_path)

def transcribe_audio(file_path: str) -> str:
    """Transcribes audio using OpenAI Whisper."""
    result = whisper_model.transcribe(file_path)
    return result["text"]

# Main Function to Run the Bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))  # Handle voice messages

    app.run_polling()

if __name__ == "__main__":
    main()
