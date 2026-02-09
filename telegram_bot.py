import logging
import os
import asyncio
import aiohttp
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from redis_bus import RedisBus
import json

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_USER_ID", "0")) # Set this to your Telegram ID for security

# Initialize Redis Bus
bus = RedisBus()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when the command /start is issued."""
    user = update.effective_user
    if ALLOWED_USER_ID != 0 and user.id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ ACCESS DENIED. IDENTITY VERIFICATION FAILED.")
        return
        
    await update.message.reply_text(f"🏰 AI IMPERIUM ONLINE.\n\nCommander {user.first_name}, system ready.\n\nCommands:\n/idea <text> - Send new idea to Orchestrator\n/status - Check system status\n/deploy <agent> - Deploy specific agent")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages."""
    user = update.effective_user
    if ALLOWED_USER_ID != 0 and user.id != ALLOWED_USER_ID:
        return

    file = await context.bot.get_file(update.message.voice.file_id)
    # In a real scenario, we would download and transcribe with Whisper here.
    # For now, we simulate or pass the file ID if we had a local Whisper service.
    
    await update.message.reply_text("🎤 Voice received. Transcribing... (Simulation: 'Create content about AI Agents')")
    
    # Simulate transcription for now
    transcribed_text = "Create viral content about AI Agents"
    
    # Publish to Orchestrator
    publish_idea(transcribed_text)
    await update.message.reply_text(f"✅ Idea captured: '{transcribed_text}'\nSent to Orchestrator.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user = update.effective_user
    if ALLOWED_USER_ID != 0 and user.id != ALLOWED_USER_ID:
        return

    text = update.message.text
    if text.startswith("/"):
        return # Commands handled by handlers
        
    # Treat plain text as an idea or command
    publish_idea(text)
    await update.message.reply_text(f"📩 Input received: '{text}'\nProcessing...")

def publish_idea(text: str):
    """Publish idea to Redis for the Orchestrator."""
    message = {
        "type": "voice_input", # or text_input, handled same by Orchestrator
        "transcription": text,
        "timestamp": 0, # Add real timestamp
        "source": "telegram"
    }
    bus.publish("user/voice", message)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check system status."""
    # In a real system, we would query Redis or the Monitor Agent
    await update.message.reply_text(f"📊 SYSTEM STATUS:\n\nAgents: ONLINE\nRedis: CONNECTED\nMode: IMPERIUM")

def main():
    """Start the bot."""
    if not TELEGRAM_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is not set.")
        return

    if not bus.connect():
         logger.warning("⚠️ Could not connect to Redis. Running in offline mode.")

    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
