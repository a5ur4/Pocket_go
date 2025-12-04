import logging
import httpx
import dotenv
import os
import sys
from urllib.parse import quote_plus, urlencode
from typing import Optional, Dict, Any

# Add parent directory to path
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
    ConversationHandler,
    filters
)

from lang_texts import lang_texts
from utils.logger import APILogger

dotenv.load_dotenv()

# --- Configuration ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
NGROK_URL = os.getenv("NGROK_URL", API_BASE_URL)

# Conversation states
RATING, COMMENT = range(2)

if not TELEGRAM_BOT_TOKEN:
    logger.critical("TELEGRAM_BOT_TOKEN is required.")
    sys.exit(1)

# --- Service Layer (API Logic) ---
class HotelApiService:
    """Handles all interactions with the backend API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.timeout = 10.0

    async def get_hotels(self, lat: float, lon: float, hotel_type: str = None) -> list:
        url = f"{self.base_url}/hotels/nearby/"
        if hotel_type:
            url += f"type/{hotel_type}"
        
        params = {"latitude": lat, "longitude": lon, "max_distance_km": 10, "limit": 10}
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()

    async def get_hotel_details(self, hotel_id: str) -> Optional[Dict]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.get(f"{self.base_url}/hotels/{hotel_id}")
            if resp.status_code == 200:
                return resp.json()
        return None

    async def get_or_create_user(self, telegram_id: int, phone: str = None) -> Optional[str]:
        """Returns the backend UUID for the user."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # 1. Try fetch
            resp = await client.get(f"{self.base_url}/users/telegram/{telegram_id}")
            if resp.status_code == 200:
                return resp.json()["id"]
            
            # 2. Create if not exists
            payload = {"telegram_id": str(telegram_id), "phone": None}
            resp = await client.post(f"{self.base_url}/users/", json=payload)
            if resp.status_code == 201:
                return resp.json()["id"]
                
        logger.error(f"Failed to get/create user for TG ID {telegram_id}")
        return None

    async def submit_evaluation(self, data: Dict) -> bool:
        url = f"{self.base_url}/evaluations/"
        logger.info(f"🚀 TENTANDO ENVIAR POST PARA: {url}")
        logger.info(f"📦 PAYLOAD: {data}")
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=data)
                
                logger.info(f"📡 STATUS CODE RETORNADO: {resp.status_code}")
                if resp.status_code not in [200, 201]:
                     logger.error(f"❌ ERRO API: {resp.text}")
                
                return resp.status_code in [200, 201]
        except Exception as e:
            logger.error(f"💀 ERRO CRÍTICO NO HTTPX: {e}")
            return False

# --- Helper Functions ---

def get_lang(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if "lang" in context.user_data:
        return context.user_data["lang"]
    code = update.effective_user.language_code or "en"
    lang = "pt" if "pt" in code.lower() else "en"
    context.user_data["lang"] = lang
    return lang

def format_hotel_message(hotel_item: dict, texts: dict) -> str:
    hotel = hotel_item["hotel"]
    emoji_map = {"HOTEL": "🏨", "HOSTEL": "🏠", "POUSADA": "🏡", "RESORT": "🏖️", "MOTEL": "❤️"}
    emoji = emoji_map.get(hotel.get("type", "").upper(), "🏨")
    
    dist_km = hotel_item['distance_km']
    if dist_km < 0.1: dist_str = texts['walking_distance_texts']['very_close']
    elif dist_km < 1.0: dist_str = f"{int(dist_km*1000)}{texts['walking_distance_texts']['walking']}"
    else: dist_str = f"{dist_km:.2f} km"
    
    score = hotel.get('web_evaluation_score')
    score_display = f"{score}/5" if score else "N/A"

    return (
        f"{emoji} <b>{hotel['name']}</b>\n"
        f"📍 <i>{hotel['address']}</i>\n"
        f"{texts['distance']}: {dist_str}\n\n"
        f"{texts['desc']}: {hotel.get('description', '')[:120]}...\n"
        f"{texts['rating']}: {score_display}\n"
    )

def create_keyboard(hotel: dict, texts: dict) -> InlineKeyboardMarkup:
    # Mini App Button
    webapp_url = f"{NGROK_URL}/static/hotel_details.html?{urlencode({'hotel_id': hotel['id'], 'api_url': API_BASE_URL})}"
    
    buttons = [
        [
            InlineKeyboardButton(texts["mini_app"]["view_details"], web_app=WebAppInfo(url=webapp_url)),
            InlineKeyboardButton(texts["evaluation"]["rate_hotel"], callback_data=f"rate_{hotel['id']}")
        ]
    ]
    
    if hotel.get("address"):
        maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(hotel['name'])}"
        buttons.append([InlineKeyboardButton(texts["map"], url=maps_url)])
        
    return buttons

api_service = HotelApiService(NGROK_URL)

# --- Core Bot Handlers ---

async def fetch_and_show_hotels(update_obj, context, lat, lon, hotel_type=None):
    lang = get_lang(update_obj, context)
    texts = lang_texts[lang]
    
    try:
        hotels = await api_service.get_hotels(lat, lon, hotel_type)
        if not hotels:
            await context.bot.send_message(update_obj.effective_chat.id, texts["no_results"])
            return

        context.user_data["hotels"] = hotels
        context.user_data["page"] = 0
        await send_hotel_card(update_obj, context)
        
    except Exception as e:
        logger.error(f"Fetch error: {e}")
        await context.bot.send_message(update_obj.effective_chat.id, texts["error"])

async def send_hotel_card(update_obj, context):
    """Generic function to send or edit the hotel card."""
    hotels = context.user_data.get("hotels", [])
    page = context.user_data.get("page", 0)
    lang = get_lang(update_obj, context)
    texts = lang_texts[lang]

    if not hotels: return

    hotel_item = hotels[page]
    hotel = hotel_item["hotel"]
    
    msg_text = format_hotel_message(hotel_item, texts)

    raw_url = hotel.get("image_url")

    if raw_url and raw_url.startswith("http"):
        image_url = raw_url
    else:
        image_url = None
    
    # Buttons construction
    buttons = create_keyboard(hotel, texts)
    
    # Navigation logic
    nav_row = []
    if page > 0: nav_row.append(InlineKeyboardButton(texts["prev"], callback_data=f"page_{page-1}"))
    if page < len(hotels) - 1: nav_row.append(InlineKeyboardButton(texts["next"], callback_data=f"page_{page+1}"))
    if nav_row: buttons.append(nav_row)
    
    reply_markup = InlineKeyboardMarkup(buttons)
    caption = f"{msg_text}\n📄 {page+1}/{len(hotels)}"
    
    # Sending Logic
    chat_id = update_obj.effective_chat.id
    
    # If callback query (editing)
    if hasattr(update_obj, 'callback_query') and update_obj.callback_query:
        await update_obj.callback_query.delete_message() # Delete old to send new with potentially new photo
        func = context.bot.send_photo if image_url else context.bot.send_message
        kwargs = {"chat_id": chat_id, "reply_markup": reply_markup, "parse_mode": "HTML"}
        
        if image_url: kwargs.update({"photo": image_url, "caption": caption})
        else: kwargs.update({"text": caption})
        
        await func(**kwargs)
        
    # If fresh message
    else:
        if image_url:
            await update_obj.message.reply_photo(photo=image_url, caption=caption, reply_markup=reply_markup, parse_mode="HTML")
        else:
            await update_obj.message.reply_html(caption, reply_markup=reply_markup)

# --- Conversation: Rating ---

async def start_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    hotel_id = query.data.split("_")[1]
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    
    # Find hotel name locally to save 1 API call
    hotel_name = "Hotel"
    for h in context.user_data.get("hotels", []):
        if h["hotel"]["id"] == hotel_id:
            hotel_name = h["hotel"]["name"]
            break
            
    context.user_data["rating_session"] = {"hotel_id": hotel_id, "hotel_name": hotel_name}
    
    # Star buttons
    keyboard = [
        [InlineKeyboardButton("⭐ 1", callback_data="rating_1"), InlineKeyboardButton("⭐⭐ 2", callback_data="rating_2")],
        [InlineKeyboardButton("⭐⭐⭐ 3", callback_data="rating_3"), InlineKeyboardButton("⭐⭐⭐⭐ 4", callback_data="rating_4")],
        [InlineKeyboardButton("⭐⭐⭐⭐⭐ 5", callback_data="rating_5")],
        [InlineKeyboardButton(texts["evaluation"]["cancel"], callback_data="rating_cancel")]
    ]
    
    try:
        await query.delete_message()
    except Exception:
        pass # Ignora se já foi deletada

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=texts["evaluation"]["rate_question"].format(hotel_name=hotel_name),
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    
    return RATING

async def handle_rating_val(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "rating_cancel":
        await query.edit_message_text("❌ Cancelado.")
        return ConversationHandler.END

    rating = int(query.data.split("_")[1])
    context.user_data["rating_session"]["value"] = rating
    
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    hotel_name = context.user_data["rating_session"]["hotel_name"]

    # Botão explícito para pular (deixar em branco)
    # Nota: O texto do botão pode ser "Pular / Skip" ou "Sem comentário"
    keyboard = [[InlineKeyboardButton(texts["evaluation"]["skip"], callback_data="comment_skip")]]
    
    # Mensagem orientando o usuário
    msg_text = (
        f"<b>{hotel_name}</b>\n"
        f"Nota: {rating} ⭐\n\n"
        f"✍️ Escreva um comentário sobre sua experiência:\n"
        f"<i>(Ou clique no botão abaixo para deixar em branco)</i>"
    )
    
    await query.edit_message_text(
        msg_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    return COMMENT

async def handle_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Determine if input is text message or callback (skip button)
    comment = ""
    is_callback = False
    
    if update.callback_query:
        is_callback = True
        await update.callback_query.answer()
        if update.callback_query.data == "comment_skip":
            comment = ""
    else:
        comment = update.message.text
        
    context.user_data["rating_session"]["comment"] = comment
    
    # Execute Submission
    return await finish_evaluation(update, context, is_callback)

async def finish_evaluation(update, context, is_callback):
    logger.info("🔄 Iniciando finish_evaluation...") # DEBUG 1
    
    try:
        session = context.user_data.get("rating_session")
        if not session:
            logger.error("❌ Sessão de avaliação perdida (reinício do bot?)")
            await _respond_error(update, is_callback, "Sessão expirada. Tente novamente.")
            return ConversationHandler.END

        lang = get_lang(update, context)
        texts = lang_texts[lang]
        
        # 1. Obter Usuário
        user_uuid = context.user_data.get("backend_user_id")
        if not user_uuid:
            logger.info("👤 Buscando/Criando usuário na API...") # DEBUG 2
            # Enviamos o ID do Telegram para garantir que o usuário existe no DB
            user_uuid = await api_service.get_or_create_user(update.effective_user.id)
            
            if user_uuid:
                context.user_data["backend_user_id"] = user_uuid
            else:
                logger.error("❌ Falha ao obter ID do usuário do Backend")
                await _respond_error(update, is_callback, "Erro ao identificar usuário.")
                return ConversationHandler.END
        
        # 2. Montar Payload
        payload = {
            "hotel_id": str(session["hotel_id"]), # Força conversão para string
            "rating": float(session["value"]),    # Força float
            "comment": session.get("comment", ""),
            "author_id": str(user_uuid)           # Força conversão para string
        }
        
        logger.info("📤 Payload montado, chamando API Service...") # DEBUG 3
        
        # 3. Enviar
        success = await api_service.submit_evaluation(payload)
        
        # 4. Resposta
        if success:
            hotel_name = session["hotel_name"]
            rating = session["value"]
            comment = session.get("comment", "")
            
            # Construir mensagem de sucesso com os dados
            response_text = texts["evaluation"]["evaluation_success"].format(
            hotel_name=hotel_name,
            rating=rating,
            comment_text=comment if comment else texts["evaluation"].get("no_comment", "Sem comentário")
            )
        else:
            response_text = texts["evaluation"].get("evaluation_error", "❌ Erro ao enviar avaliação. Tente novamente.")
        if is_callback:
            await update.callback_query.edit_message_text(response_text, parse_mode="HTML")
        else:
            await update.message.reply_html(response_text)
            
    except Exception as e:
        logger.exception(f"💥 ERRO NÃO TRATADO EM FINISH_EVALUATION: {e}")
        await _respond_error(update, is_callback, "Ocorreu um erro interno.")
        
    # Limpa a sessão
    context.user_data.pop("rating_session", None)
    return ConversationHandler.END

async def _respond_error(update, is_callback, text):
    """Helper para responder erro sem duplicar código"""
    if is_callback:
        try:
            await update.callback_query.edit_message_text(f"❌ {text}")
        except:
            pass # Mensagem pode não existir
    else:
        await update.message.reply_text(f"❌ {text}")

# --- Standard Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    kb = ReplyKeyboardMarkup([[KeyboardButton(texts["button_location"], request_location=True)]], resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_html(texts["start"], reply_markup=kb)

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data["user_latitude"] = loc.latitude
    context.user_data["user_longitude"] = loc.longitude
    
    lang = get_lang(update, context)
    await update.message.reply_html(lang_texts[lang]["found"])
    await fetch_and_show_hotels(update, context, loc.latitude, loc.longitude)

async def pagination_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["page"] = int(query.data.split("_")[1])
    await send_hotel_card(update, context)
    
# --- Feature: Help Command (/help) ---
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the help message based on the current language."""
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    # Ensure your lang_texts dictionary has a "help" key
    help_text = texts.get("help", "Use /start to begin or /type to filter hotels.")
    await update.message.reply_html(help_text)

# --- Feature: Language Selection (/lang) ---
async def show_language_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows an inline menu to select the language."""
    keyboard = [
        [
            InlineKeyboardButton("🇧🇷 Português", callback_data="set_lang_pt"),
            InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    msg = "Select your language / Selecione seu idioma:"
    await update.message.reply_text(msg, reply_markup=reply_markup)

async def handle_language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the language selection callback."""
    query = update.callback_query
    await query.answer()
    
    # query.data will be "set_lang_pt" or "set_lang_en"
    chosen_lang = query.data.split("_")[-1] # Gets 'pt' or 'en'
    
    context.user_data["lang"] = chosen_lang
    
    texts = lang_texts[chosen_lang]
    confirm_msg = texts.get("lang_set", f"Language set to {chosen_lang.upper()}")
    
    # Edit the message removing buttons and confirming selection
    await query.edit_message_text(f"✅ {confirm_msg}")

# --- Feature: Hotel Type Filter (/type) ---
async def show_hotel_type_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Displays the hotel type filter menu."""
    lang = get_lang(update, context)
    texts = lang_texts[lang]
    
    # Check if we already have the user's location
    if "user_latitude" not in context.user_data:
        msg = "📍 " + texts.get("send_location_first", "Please send your location first.")
        await update.message.reply_text(msg)
        return

    # Hotel Type Buttons
    keyboard = [
        [InlineKeyboardButton("🏨 Hotel", callback_data="type_HOTEL"), InlineKeyboardButton("🏠 Hostel", callback_data="type_HOSTEL")],
        [InlineKeyboardButton("🏡 Pousada", callback_data="type_POUSADA"), InlineKeyboardButton("🏖️ Resort", callback_data="type_RESORT")],
        [InlineKeyboardButton("🏢 Apartamento", callback_data="type_APARTAMENTO"), InlineKeyboardButton("❤️ Motel", callback_data="type_MOTEL")]
    ]
    
    await update.message.reply_html(
        texts.get("select_type", "Select accommodation type:"), 
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_hotel_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Filters results by type and triggers a new fetch."""
    query = update.callback_query
    await query.answer()
    
    hotel_type = query.data.split("_")[1] # e.g., HOTEL
    
    lat = context.user_data.get("user_latitude")
    lon = context.user_data.get("user_longitude")
    
    # If location is lost (e.g., bot restart), ask again
    if not lat or not lon:
        await query.edit_message_text("⚠️ Location lost. Please send your location again.")
        return
        
    await query.edit_message_text(f"🔍 Searching for: <b>{hotel_type}</b>...", parse_mode="HTML")
    await fetch_and_show_hotels(update, context, lat, lon, hotel_type)

# --- Main ---
async def post_init_commands(app: Application):
    """Sets the Telegram blue menu commands."""
    await app.bot.set_my_commands([
        BotCommand("start", "Start / Início"),
        BotCommand("type", "Filter Type / Filtrar Tipo"),
        BotCommand("lang", "Change Language / Mudar Idioma"),
        BotCommand("help", "Help / Ajuda")
    ])

def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).post_init(post_init_commands).build()

    # --- Rating Conversation Handler ---
    rating_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_rating, pattern="^rate_")],
        states={
            RATING: [CallbackQueryHandler(handle_rating_val, pattern="^rating_")],
            COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_comment),
                CallbackQueryHandler(handle_comment, pattern="^comment_")
            ]
        },
        fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
        per_chat=True
    )

    # --- Command Handlers ---
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))      # Restored
    app.add_handler(CommandHandler("lang", show_language_menu)) # Restored
    app.add_handler(CommandHandler("type", show_hotel_type_menu)) # Restored

    # --- Message Handlers ---
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # --- Callback Handlers ---
    # Pagination (matches "page_0", "page_1"...)
    app.add_handler(CallbackQueryHandler(pagination_handler, pattern="^page_"))
    
    # Type Selection (matches "type_HOTEL", "type_MOTEL"...)
    app.add_handler(CallbackQueryHandler(handle_hotel_type_selection, pattern="^type_"))
    
    # Language Selection (matches "set_lang_pt", "set_lang_en"...)
    app.add_handler(CallbackQueryHandler(handle_language_selection, pattern="^set_lang_"))

    # Rating Handler (Keep last to avoid conflict if patterns were generic)
    app.add_handler(rating_conv)
    
    logger.info("Bot is running with all features restored...")
    app.run_polling()

if __name__ == "__main__":
    main()