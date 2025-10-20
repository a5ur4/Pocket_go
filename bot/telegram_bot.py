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
    welcome_message = (
        f"🎒 Welcome to <b>Pocket GO Bot</b>, {user.mention_html()}!\n\n"
        f"🏨 I'm your travel companion for finding the perfect accommodations wherever you go!\n\n"
        f"<b>What I can do:</b>\n"
        f"📍 Find hotels near your location\n"
        f"🗺️ Search accommodations in any city\n"
        f"📱 Get personalized recommendations\n\n"
        f"<b>Getting started:</b>\n"
        f"• Share your location 📍 for instant nearby results (10 closest accommodations)\n"
        f"• Type /help for all available commands\n"
        f"• Just tell me where you are, and I'll find the best places to stay!"
    )
    await update.message.reply_html(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a help message when the /help command is issued."""
    help_text = (
        f"🤖 <b>Pocket GO Bot - Help Guide</b>\n\n"
        f"<b>📋 Available Commands:</b>\n"
        f"• /start - Welcome message and bot introduction\n"
        f"• /help - Show this help guide\n\n"
        f"<b>📍 Location Features:</b>\n"
        f"• Share your location 📍 - Get 10 closest accommodations instantly\n"
        f"• Get precise latitude and longitude coordinates\n\n"
        f"<b>🔍 Search Options:</b>\n"
        f"• 'Find hotels in [city]' - Search accommodations in any city\n"
        f"• 'Find cities near [location]' - Discover nearby destinations\n\n"
        f"<b>💡 Tips:</b>\n"
        f"• Use the location sharing button for accurate results\n"
        f"• Type city names clearly for better search results\n"
        f"• All searches provide detailed accommodation information\n\n"
        f"<i>Happy travels! 🧳✈️</i>"
    )
    await update.message.reply_html(help_text)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle location messages sent by the user to take his location."""
    if update.message.location:
        latitude = update.message.location.latitude
        longitude = update.message.location.longitude
        logger.info(
            f"Recived location from user {update.effective_user.id}: "
            f"Latitude: {latitude}, Longitude: {longitude}"
        )
        
        await update.message.reply_text(
            f"Thanks for sharing your location! "
            f"I received Latitude: {latitude}, Longitude: {longitude}."
        )
    else:
        await update.message.reply_text(
            "Please send a valid location."
        )

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
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Start the bot
    logger.info("Starting the Telegram bot...")
    application.run_polling()

if __name__ == '__main__':
    main()