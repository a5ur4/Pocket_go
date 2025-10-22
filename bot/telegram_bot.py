import logging
import httpx
import dotenv
import os

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

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
RESULTS_PER_PAGE = 5

# 🌎 Multi-language texts
lang_texts = {
    "pt": {
        "found": "🗺️ <b>Encontrei acomodações perto de você!</b>\n\nAqui estão as mais próximas:",
        "no_results": "😕 Não encontrei acomodações próximas à sua localização.",
        "error": "⚠️ Erro ao conectar ao serviço de acomodações. Tente novamente mais tarde.",
        "distance": "📏 Distância",
        "rating": "⭐ Avaliação",
        "type": "🏢 Tipo",
        "desc": "📝 Descrição",
        "phone": "📞 Telefone",
        "site": "🌐 Abrir site",
        "map": "📍 Ver no mapa",
        "prev": "⬅️ Anterior",
        "next": "➡️ Próximo",
        "lang_set": "✅ Idioma alterado para <b>Português 🇧🇷</b>.",
        "lang_invalid": "❌ Idioma inválido. Use /lang pt ou /lang en.",
        "start": "🎒 Bem-vindo ao <b>Pocket GO Bot</b>!\n\nEnvie sua localização 📍 para descobrir acomodações próximas.",
        "help": (
            "🤖 <b>Ajuda do Pocket GO Bot</b>\n\n"
            "/start - Iniciar o bot e obter instruções\n"
            "/lang [pt|en] - Definir seu idioma preferido para Português ou Inglês\n"
            "/type - Escolher tipo específico de acomodação\n\n"
            "📍 Envie sua localização para encontrar acomodações próximas\n"
            "🏨 Use /type + sua localização para filtrar por tipo específico"
        ),
        "walking_distance_texts": {
            "very_close": "Muito perto (menos de 100m) 🚶‍♂️",
            "close": "m de distância 🚶‍♂️",
            "walking": "m, consegue ir caminhando 🚶‍♂️"
        },
        "select_type": "🏨 <b>Escolha o tipo de acomodação:</b>\n\nSelecione o tipo que você está procurando:",
        "type_search": "🔍 Procurando por <b>{type}</b> próximos à sua localização..."
    },
    "en": {
        "found": "🗺️ <b>Found accommodations near your location!</b>\n\nHere are the closest ones:",
        "no_results": "😕 I couldn't find accommodations near your location.",
        "error": "⚠️ Error connecting to the accommodation service. Please try again later.",
        "distance": "📏 Distance",
        "rating": "⭐ Rating",
        "type": "🏢 Type",
        "desc": "📝 Description",
        "phone": "📞 Phone",
        "site": "🌐 Open website",
        "map": "📍 View on map",
        "prev": "⬅️ Previous",
        "next": "➡️ Next",
        "lang_set": "✅ Language changed to <b>English 🇺🇸</b>.",
        "lang_invalid": "❌ Invalid language. Use /lang pt or /lang en.",
        "start": "🎒 Welcome to <b>Pocket GO Bot</b>!\n\nSend your location 📍 to find nearby accommodations.",
        "help": (
            "🤖 <b>Pocket GO Bot Help</b>\n\n"
            "/start - Start the bot and get instructions\n"
            "/lang [pt|en] - Set your preferred language to Portuguese or English\n"
            "/type - Choose specific accommodation type\n\n"
            "📍 Send your location to find nearby accommodations\n"
            "🏨 Use /type + your location to filter by specific type"
        ),
        "walking_distance_texts": {
            "very_close": "Very close (less than 100m) 🚶‍♂️",
            "close": "m away 🚶‍♂️",
            "walking": "m Walking distance 🚶‍♂️"
        },
        "select_type": "🏨 <b>Choose accommodation type:</b>\n\nSelect the type you're looking for:",
        "type_search": "🔍 Searching for <b>{type}</b> near your location..."
    },
}

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
    if hotel.get("website"):
        buttons.append(InlineKeyboardButton(texts["site"], url=hotel["website"]))

    # Use the address is not the best way, but it works better than the location field
    if hotel.get("address"):
        maps_url = f"https://www.google.com/maps/search/?api=1&query={hotel['address'].replace(' ', '+')}"
        buttons.append(InlineKeyboardButton(texts["map"], url=maps_url))
        
    return [buttons] if buttons else []


async def send_hotels_page(update_or_query, context, page, texts):
    """Send one page of hotel results"""
    hotels_data = context.user_data["hotels"]
    total_pages = (len(hotels_data) + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE

    start = page * RESULTS_PER_PAGE
    end = start + RESULTS_PER_PAGE
    hotels_slice = hotels_data[start:end]

    # Store message IDs for later deletion
    message_ids = []
    
    for item in hotels_slice:
        hotel = item["hotel"]
        msg = format_hotel_message(item, texts)
        reply_markup = InlineKeyboardMarkup(create_buttons(hotel, texts))
        sent_message = await update_or_query.message.reply_html(msg, reply_markup=reply_markup)
        message_ids.append(sent_message.message_id)

    # Pagination buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(texts["prev"], callback_data=f"page_{page-1}")
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(texts["next"], callback_data=f"page_{page+1}")
        )

    if nav_buttons:
        sent_message = await update_or_query.message.reply_text(
            f"📄 {page+1}/{total_pages}",
            reply_markup=InlineKeyboardMarkup([nav_buttons]),
        )
        message_ids.append(sent_message.message_id)
    
    # Store message IDs in context for deletion on next page
    context.user_data["message_ids"] = message_ids


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
        await send_hotels_page(update, context, 0, texts)

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
    
    # Delete previous messages (hotels and pagination button)
    if "message_ids" in context.user_data:
        for msg_id in context.user_data["message_ids"]:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
            except Exception as e:
                logger.debug(f"Could not delete message {msg_id}: {e}")
    
    # Delete the pagination button message that was clicked
    try:
        await query.message.delete()
    except Exception as e:
        logger.debug(f"Could not delete pagination message: {e}")
    
    # Send new page
    await send_hotels_page(query, context, page, texts)

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
        await query.edit_message_text("❌ Location not found. Please send your location again.")
        return
    
    # Show search message
    type_display = {
        "HOTEL": "Hotels 🏨",
        "HOSTEL": "Hostels 🏠", 
        "POUSADA": "Pousadas 🏡",
        "RESORT": "Resorts 🏖️",
        "APARTAMENTO": "Apartments 🏢",
        "MOTEL": "Motels ❤️"
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
        await send_hotels_page(query, context, 0, texts)

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

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

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
