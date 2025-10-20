import asyncio
import logging
import httpx
import dotenv
import os

dotenv.load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! Welcome to Pocket GO Bot. \n"
        f"I can help you find hotels and cities. Use /help to see available commands."
        f"Send hello world to see if i'm working!"
    )
    
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_text = (
        "Available commands:\n"
        "/start - Start the bot and get a welcome message\n"
        "/help - Show this help message\n"
        "You can also send messages like 'Find hotels in [city]' or 'Find cities near [location]'."
    )
    await update.message.reply_text(help_text)

# Need to implement the nearby search functionality later and other
# But for now just a placeholder is enough

def main() -> None:
    """Start the Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables.")
        return

    # Build the application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Start the bot
    logger.info("Starting the Telegram bot...")
    application.run_polling()

if __name__ == '__main__':
    main()