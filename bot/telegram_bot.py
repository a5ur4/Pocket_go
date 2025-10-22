import logging
import httpx
import dotenv
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from urllib.parse import quote_plus

from lang_texts import lang_texts

dotenv.load_dotenv()

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL")

# Config
RESULTS_PER_PAGE = 1

def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the user's preferred language or fallback to auto-detect."""
    if "lang" in context.user_data:
        return context.user_data["lang"]

    code = update.effective_user.language_code or "en"
    lang = "pt" if "pt" in code.lower() else "en"
    context.user_data["lang"] = lang
    return lang


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lang command (manual language selection)."""
    if not context.args:
        await update.message.reply_text("Usage: /lang [pt|en]")
        return

    chosen = context.args[0].lower()
    if chosen in ["pt", "en"]:
        context.user_data["lang"] = chosen
        texts = lang_texts[chosen]
        await update.message.reply_html(texts["lang_set"])
    else:
        lang = get_lang(update, context)
        texts = lang_texts[lang]
        await update.message.reply_html(texts["lang_invalid"])


def format_hotel_message(hotel_item, texts):
    """Format hotel info for display"""
    hotel = hotel_item["hotel"]
    emoji_map = {
        "HOTEL": "🏨",
        "HOSTEL": "🏠",
        "POUSADA": "🏡",
        "RESORT": "🏖️",
        "APARTAMENTO": "🏢",
        "MOTEL": "❤️",
    }
    emoji = emoji_map.get(hotel["type"], "🏨")

    # Custom text for small distances
    distance_km = hotel_item['distance_km']
    if distance_km < 0.1:
        distance_text = texts['walking_distance_texts']['very_close']
    elif distance_km < 0.5:
        distance_text = f"{int(distance_km * 1000)}{texts['walking_distance_texts']['close']}"
    elif distance_km < 1.0:
        distance_text = f"{int(distance_km * 1000)}{texts['walking_distance_texts']['walking']}"
    else:
        distance_text = f"{distance_km:.2f} km"
    
    return (
        f"{emoji} <b>{hotel['name']}</b>\n"
        f"📍 <i>{hotel['address']}</i>\n"
        f"{texts['distance']}: {distance_text}\n\n"
        f"{texts['desc']}: {hotel['description']}\n"
        f"{texts['type']}: {hotel['type']}\n"
        f"{texts['rating']}: {hotel['web_evaluation_score']}/10\n"
        f"{texts['phone']}: {hotel.get('phone') or '—'}"
    )

def create_buttons(hotel, texts):
    """Generate action buttons for each hotel"""
    buttons = []
    
    # Website button
    if hotel.get("website"):
        buttons.append(InlineKeyboardButton(texts["site"], url=hotel["website"]))

    # Google Maps button
    if hotel.get("address"):
        encoded_address = quote_plus(hotel["address"])
        maps_url = f"https://www.google.com/maps/search/?api=1&query={encoded_address}"
        buttons.append(InlineKeyboardButton(texts["map"], url=maps_url))
    
    return buttons


async def send_or_edit_hotel_page(update_or_query, context, page, texts):
    """Send or edit one page of hotel results"""
    hotels_data = context.user_data["hotels"]
    total_hotels = len(hotels_data)
    
    hotel_item = hotels_data[page]
    hotel = hotel_item["hotel"]
    
    # Format message
    msg_content = format_hotel_message(hotel_item, texts)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(texts["prev"], callback_data=f"page_{page-1}")
        )
    if page < total_hotels - 1:
        nav_buttons.append(
            InlineKeyboardButton(texts["next"], callback_data=f"page_{page+1}")
        )
    
    action_buttons = create_buttons(hotel, texts)
    
    keyboard = []
    if action_buttons:
        keyboard.append(action_buttons)
    if nav_buttons:
        keyboard.append(nav_buttons)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    is_query = isinstance(update_or_query, Update) and update_or_query.callback_query
    
    msg_with_counter = f"{msg_content}\n\n📄 {page+1}/{total_hotels}"
    
    if is_query:
        query = update_or_query.callback_query
        try:
            await query.edit_message_text(
                msg_with_counter,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.debug(f"Could not edit message: {e}")
    else:
        await update_or_query.message.reply_html(
            msg_with_counter,
            reply_markup=reply_markup
        )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user location and show nearby hotels"""
    if not update.message.location:
        await update.message.reply_text("Please send a valid location.")
        return

    lang = get_lang(update, context)
    texts = lang_texts[lang]
    latitude = update.message.location.latitude
    longitude = update.message.location.longitude
    
    # Store user location for later use
    # I almost forgot to do this, without it, the /type command would not work
    context.user_data["user_latitude"] = latitude
    context.user_data["user_longitude"] = longitude

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/hotels/nearby/?latitude={latitude}&longitude={longitude}&max_distance_km=10&limit=10"
            )
            response.raise_for_status()
            hotels_data = response.json()

        if not hotels_data:
            await update.message.reply_text(texts["no_results"])
            return

        context.user_data["hotels"] = hotels_data
        context.user_data["page"] = 0

        await update.message.reply_html(texts["found"])
        await send_or_edit_hotel_page(update, context, 0, texts)

    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        await update.message.reply_text(texts["error"])


async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle pagination button callbacks"""
    query = update.callback_query
    await query.answer()

    page = int(query.data.split("_")[1])
    lang = get_lang(update, context)
    texts = lang_texts[lang]

    context.user_data["page"] = page
    
    await send_or_edit_hotel_page(update, context, page, texts)

async def show_hotel_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show hotel type selection menu after receiving location"""
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    
    # Create inline keyboard with hotel types
    keyboard = [
        [
            InlineKeyboardButton("🏨 Hotel", callback_data="type_HOTEL"),
            InlineKeyboardButton("🏠 Hostel", callback_data="type_HOSTEL"),
        ],
        [
            InlineKeyboardButton("🏡 Pousada", callback_data="type_POUSADA"),
            InlineKeyboardButton("🏖️ Resort", callback_data="type_RESORT"),
        ],
        [
            InlineKeyboardButton("🏢 Apartamento", callback_data="type_APARTAMENTO"),
            InlineKeyboardButton("❤️ Motel", callback_data="type_MOTEL"),
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_html(texts["select_type"], reply_markup=reply_markup)


async def handle_hotel_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle hotel type selection and search nearby hotels"""
    query = update.callback_query
    await query.answer()
    
    # Extract hotel type from callback data
    hotel_type = query.data.split("_")[1]
    print( hotel_type)
    
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    
    # Get stored location
    latitude = context.user_data.get("user_latitude")
    longitude = context.user_data.get("user_longitude")
    
    if not latitude or not longitude:
        await query.edit_message_text(texts["type_select"]["location_error"])
        return
    
    # Show search message
    type_display = {
        "HOTEL":  texts["accommodation_types"]["hotel"]+" 🏨",
        "HOSTEL": texts["accommodation_types"]["hostel"]+" 🏠",
        "POUSADA": texts["accommodation_types"]["Pousada"]+" 🏡",
        "RESORT": texts["accommodation_types"]["Resort"]+" 🏖️",
        "APARTAMENTO": texts["accommodation_types"]["Apartamento"]+" 🏢",
        "MOTEL": texts["accommodation_types"]["Motel"]+" ❤️"
    }

    await query.edit_message_text(
        texts["type_search"].format(type=type_display.get(hotel_type, hotel_type))
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE_URL}/hotels/nearby/type/{hotel_type}?latitude={latitude}&longitude={longitude}&max_distance_km=10&limit=10"
            )
            response.raise_for_status()
            hotels_data = response.json()

        if not hotels_data:
            await query.message.reply_text(texts["no_results"])
            return

        context.user_data["hotels"] = hotels_data
        context.user_data["page"] = 0

        await query.message.reply_html(texts["found"])
        await send_or_edit_hotel_page(query, context, 0, texts)

    except httpx.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        await query.message.reply_text(texts["error"])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    await update.message.reply_html(texts["start"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    await update.message.reply_html(texts["help"])

async def post_init(application: Application):
    """Define the bot post-initialization actions, like the commands list"""

    # Use Portuguese as default for command descriptions since we don't have user context here
    default_texts = lang_texts["pt"]
    await application.bot.set_my_commands([
        BotCommand("start", default_texts["post_init"]["start"]),
        BotCommand("help", default_texts["post_init"]["help"]),
        BotCommand("lang", default_texts["post_init"]["lang"]),
        BotCommand("type", default_texts["post_init"]["type"])
    ])

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    app = (
        ApplicationBuilder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", set_language))
    app.add_handler(CommandHandler("type", show_hotel_type_menu))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern="^page_"))
    app.add_handler(CallbackQueryHandler(handle_hotel_type_selection, pattern="^type_"))

    logger.info("Bot running with multilingual support...")
    app.run_polling()


if __name__ == "__main__":
    main()
