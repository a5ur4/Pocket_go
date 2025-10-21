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
RESULTS_PER_PAGE = 3

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
            "/lang [pt|en] - Definir seu idioma preferido para Português ou Inglês\n\n"
            "Para encontrar acomodações próximas, basta enviar sua localização 📍."
        )
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
            "/lang [pt|en] - Set your preferred language to Portuguese or English\n\n"
            "To find nearby accommodations, simply send your location 📍."
        )
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

    return (
        f"{emoji} <b>{hotel['name']}</b>\n"
        f"📍 <i>{hotel['address']}</i>\n"
        f"{texts['distance']}: {hotel_item['distance_km']:.2f} km\n\n"
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

    for item in hotels_slice:
        hotel = item["hotel"]
        msg = format_hotel_message(item, texts)
        reply_markup = InlineKeyboardMarkup(create_buttons(hotel, texts))
        await update_or_query.message.reply_html(msg, reply_markup=reply_markup)

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
        await update_or_query.message.reply_text(
            f"📄 {page+1}/{total_pages}",
            reply_markup=InlineKeyboardMarkup([nav_buttons]),
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
    # Delete previous messages
    if "message_ids" in context.user_data:
        for msg_id in context.user_data["message_ids"]:
            try:
                await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
            except Exception:
                pass  # Message might already be deleted
    await query.message.delete()
    await send_hotels_page(query, context, page, texts)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    await update.message.reply_html(texts["start"])

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    help_text = (
        "🤖 <b>Pocket GO Bot Help</b>\n\n"
        "/start - Start the bot and get instructions\n"
        "/lang [pt|en] - Set your preferred language to Portuguese or English\n\n"
        "To find nearby accommodations, simply send your location 📍."
    )
    await update.message.reply_html(help_text)

def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set.")
        return

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("lang", set_language))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern="^page_"))

    logger.info("Bot running with multilingual support...")
    app.run_polling()


if __name__ == "__main__":
    main()
