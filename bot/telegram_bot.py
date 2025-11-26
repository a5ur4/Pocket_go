import logging
import httpx
import dotenv
import os
import sys
from urllib.parse import quote_plus, urlencode

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    KeyboardButton,
    ReplyKeyboardMarkup,
    WebAppInfo
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from lang_texts import lang_texts
from utils.logger import APILogger

dotenv.load_dotenv()

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Constants
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
NGROK_URL = os.getenv("NGROK_URL", API_BASE_URL)

if not TELEGRAM_BOT_TOKEN:
    logger.critical("TELEGRAM_BOT_TOKEN is required but not set")
    sys.exit(1)

# --- Helper Functions ---

def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get the user's preferred language or fallback to auto-detect."""
    if "lang" in context.user_data:
        return context.user_data["lang"]

    code = update.effective_user.language_code or "en"
    lang = "pt" if "pt" in code.lower() else "en"
    context.user_data["lang"] = lang
    return lang

def format_hotel_message(hotel_item, texts):
    """Format hotel info for display in the chat card"""
    hotel = hotel_item["hotel"]
    
    # Simple emoji mapping
    emoji_map = {
        "HOTEL": "🏨", "HOSTEL": "🏠", "POUSADA": "🏡",
        "RESORT": "🏖️", "APARTAMENTO": "🏢", "MOTEL": "❤️",
    }
    emoji = emoji_map.get(hotel.get("type", "").upper(), "🏨")

    distance_km = hotel_item['distance_km']
    
    # Helper for distance formatting
    if distance_km < 0.1:
        dist_str = texts['walking_distance_texts']['very_close']
    elif distance_km < 0.5:
        dist_str = f"{int(distance_km * 1000)}{texts['walking_distance_texts']['close']}"
    elif distance_km < 1.0:
        dist_str = f"{int(distance_km * 1000)}{texts['walking_distance_texts']['walking']}"
    else:
        dist_str = f"{distance_km:.2f} km"
    
    return (
        f"{emoji} <b>{hotel['name']}</b>\n"
        f"📍 <i>{hotel['address']}</i>\n"
        f"{texts['distance']}: {dist_str}\n\n"
        f"{texts['desc']}: {hotel.get('description', '')[:100]}...\n" # Truncate desc for cleaner chat UI
        f"{texts['rating']}: {hotel.get('web_evaluation_score', 'N/A')}/5\n"
    )

def create_buttons(hotel, texts):
    """Generate action buttons including the Mini App link"""
    buttons = []
    
    # 1. URL do Mini App
    base_webapp_url = f"{NGROK_URL}/static/hotel_details.html"
    query_params = {
        'hotel_id': hotel['id'],
        'api_url': API_BASE_URL
    }
    full_webapp_url = f"{base_webapp_url}?{urlencode(query_params)}"
    
    # 2. Botão principal (Mini App)
    mini_app_button = InlineKeyboardButton(
        text=texts["mini_app"]["view_details"],
        web_app=WebAppInfo(url=full_webapp_url)
    )
    
    row1 = [mini_app_button]
    
    buttons.append(row1)
    
    # 3. Botão do Google Maps
    if hotel.get("name") and hotel.get("address"):
        encoded_address = quote_plus(hotel["address"])
        name = quote_plus(hotel["name"])
        maps_url = f"https://www.google.com/maps/search/?api=1&query={name}"
        buttons.append([InlineKeyboardButton(text=texts["map"], url=maps_url)])
    
    return buttons

def generate_hotel_image(hotel):
    """Validate and return hotel image URL"""
    img = hotel.get("image_url")
    if img and isinstance(img, str) and img.startswith(('http://', 'https://')):
        return img.strip()
    return None

# --- Async Handlers ---

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /lang command"""
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

async def send_or_edit_hotel_page_with_image(update_or_query, context, page, texts):
    """Render the hotel card with navigation"""
    hotels_data = context.user_data.get("hotels", [])
    if not hotels_data:
        return 

    total_hotels = len(hotels_data)
    hotel_item = hotels_data[page]
    hotel = hotel_item["hotel"]
    
    msg_content = format_hotel_message(hotel_item, texts)
    image_url = generate_hotel_image(hotel)
    
    # Navigation Buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(texts["prev"], callback_data=f"page_{page-1}"))
    if page < total_hotels - 1:
        nav_buttons.append(InlineKeyboardButton(texts["next"], callback_data=f"page_{page+1}"))
    
    # Combine Action + Nav buttons
    keyboard = create_buttons(hotel, texts)
    if nav_buttons:
        keyboard.append(nav_buttons)
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg_caption = f"{msg_content}\n📄 {page+1}/{total_hotels}"
    
    # Logic to handle both Message (new) and CallbackQuery (edit)
    is_query = isinstance(update_or_query, Update) and update_or_query.callback_query
    
    try:
        if is_query:
            query = update_or_query.callback_query
            # Telegram doesn't support editing a text msg into a photo msg easily. 
            # We delete and send new.
            await query.delete_message()
            if image_url:
                await context.bot.send_photo(
                    chat_id=query.message.chat_id,
                    photo=image_url,
                    caption=msg_caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=msg_caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
        else:
            # First interaction
            if image_url:
                await update_or_query.message.reply_photo(
                    photo=image_url,
                    caption=msg_caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
            else:
                await update_or_query.message.reply_html(
                    msg_caption,
                    reply_markup=reply_markup
                )
    except Exception as e:
        logger.error(f"Error sending message: {e}")

async def fetch_and_show_hotels(update_or_query, context, latitude, longitude, hotel_type=None):
    """Core logic to fetch from API"""
    lang = get_lang(update_or_query, context)
    texts = lang_texts[lang]

    # Clean URL construction
    base_url = f"{API_BASE_URL}/hotels/nearby/"
    if hotel_type:
        base_url += f"type/{hotel_type}"
    
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "max_distance_km": 10,
        "limit": 10
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            hotels_data = response.json()

        if not hotels_data:
            # Determine correct chat_id object
            chat_id = update_or_query.effective_chat.id
            await context.bot.send_message(chat_id=chat_id, text=texts["no_results"])
            return

        context.user_data["hotels"] = hotels_data
        context.user_data["page"] = 0
        
        # Trigger display
        await send_or_edit_hotel_page_with_image(update_or_query, context, 0, texts)

    except httpx.HTTPError as e:
        logger.error(f"API Error: {e}")
        chat_id = update_or_query.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text=texts["error"])

# --- Command Handlers ---

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.location:
        await update.message.reply_text("Please send a valid location.")
        return

    lang = get_lang(update, context)
    texts = lang_texts[lang]
    lat = update.message.location.latitude
    lon = update.message.location.longitude
    
    # Store location for /type command usage later
    context.user_data["user_latitude"] = lat
    context.user_data["user_longitude"] = lon
    
    APILogger.log_telegram_bot_action(
        action="LOCATION_SHARED",
        user_id=update.effective_user.id,
        username=update.effective_user.username,
        details={"lat": lat, "lon": lon, "lang": lang}
    )

    await update.message.reply_html(texts["found"])
    await fetch_and_show_hotels(update, context, lat, lon)

async def show_hotel_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    
    # Check if we have location
    if "user_latitude" not in context.user_data:
        await update.message.reply_text(texts.get("send_location_first", "Please send location first!"))
        return

    keyboard = [
        [InlineKeyboardButton("🏨 Hotel", callback_data="type_HOTEL"), InlineKeyboardButton("🏠 Hostel", callback_data="type_HOSTEL")],
        [InlineKeyboardButton("🏡 Pousada", callback_data="type_POUSADA"), InlineKeyboardButton("🏖️ Resort", callback_data="type_RESORT")],
        [InlineKeyboardButton("🏢 Apartamento", callback_data="type_APARTAMENTO"), InlineKeyboardButton("❤️ Motel", callback_data="type_MOTEL")]
    ]
    
    await update.message.reply_html(texts["select_type"], reply_markup=InlineKeyboardMarkup(keyboard))

async def handle_hotel_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    hotel_type = query.data.split("_")[1]
    lat = context.user_data.get("user_latitude")
    lon = context.user_data.get("user_longitude")
    
    if not lat or not lon:
        await query.edit_message_text("Location lost. Please send location again.")
        return
        
    await fetch_and_show_hotels(update, context, lat, lon, hotel_type)

async def handle_pagination(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    page = int(query.data.split("_")[1])
    lang = get_lang(update, context)
    context.user_data["page"] = page
    await send_or_edit_hotel_page_with_image(update, context, page, lang_texts[lang])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    
    btn = KeyboardButton(text=texts["button_location"], request_location=True)
    kb = ReplyKeyboardMarkup([[btn]], resize_keyboard=True, one_time_keyboard=True)
    
    await update.message.reply_html(texts["start"], reply_markup=kb)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    await update.message.reply_html(lang_texts[lang]["help"])

async def post_init(application: Application):
    await application.bot.set_my_commands([
        BotCommand("start", "Início / Start"),
        BotCommand("help", "Ajuda / Help"),
        BotCommand("type", "Filtrar Tipo / Filter Type"),
        BotCommand("lang", "Mudar Idioma / Change Language")
    ])

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", set_language))
    app.add_handler(CommandHandler("type", show_hotel_type_menu))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern="^page_"))
    app.add_handler(CallbackQueryHandler(handle_hotel_type_selection, pattern="^type_"))

    logger.info("Bot started successfully")
    app.run_polling()

if __name__ == "__main__":
    main()