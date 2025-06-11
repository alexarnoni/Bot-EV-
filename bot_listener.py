import os
import json
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes,MessageHandler, CallbackQueryHandler, filters
from scanner import scan_apostas

# Configurar logging (arquivo + terminal)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("listener.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logging.info("🔊 bot_listener.py iniciado.")

# Carregar variáveis de ambiente
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# ----- Carregar ou iniciar filtros salvos -----
try:
    with open("filtros_por_chat.json", "r", encoding="utf-8") as f:
        filtros_por_chat = json.load(f)
except Exception:
    filtros_por_chat = {}
    logging.warning("⚠️ Nenhum filtro salvo encontrado. Iniciando com dicionário vazio.")

def salvar_filtros():
    with open("filtros_por_chat.json", "w", encoding="utf-8") as f:
        json.dump(filtros_por_chat, f, indent=2, ensure_ascii=False)

# ----- LISTAS DE LIGAS -----

ligas_brasil = [
    "Brazil - Serie A",
    "Brazil - Serie B",
    "Brazil - Serie D",
    "Brazil - Paulista Serie B",
    "Brazil - Baiano 2",
    "Brazil - Paranaense 2",
    "Brazil - Copa Do Nordeste",
    "Brazil - Catarinense U20",
    "Brazil - Brasileiro Women",
    "Brazil - Brasileiro Women A3",
    "Brazil - Brasileiro Women A2",
    "Brazil - Goiano 2",
    "Brazil - Paulista U20",
    "Brazil - Campeonato Brasileiro",
]

ligas_america_sul = [
    "Argentina - Primera B Metropolitana",
    "Argentina - Primera B Nacional",
    "Argentina - Liga Nacional",
    "Argentina - Torneo Federal A",
    "Argentina - La Liga",
    "Bolivia - Primera Division",
    "Chile - Cup",
    "Chile - LNB Segunda",
    "Chile - Primera Division Women",
    "Colombia - Primera A",
    "Colombia - Primera B",
    "Colombia - Liga Women",
    "Ecuador - Primera Women",
    "Ecuador - Serie A",
    "Paraguay - Women League",
    "Peru - Liga 1",
    "Peru - Liga 2",
    "Uruguay - Amateur Cup",
    "Uruguay - Liga Femenina",
    "Uruguay - Primera Division",
    "Uruguay - Segunda Division",
    "Uruguay - Segunda B Nacional",
    "Venezuela - Primera Division",
    "Venezuela - Segunda Division",
]

ligas_europa = [
    "Germany - Bundesliga",
    "Spain - Tercera Division",
    "Spain - Segunda Division",
    "France - Division 1",
    "France - Division 1 Women",
    "Italy - Serie A2",
    "Sweden - Allsvenskan",
    "Sweden - Superettan",
    "Sweden - Damallsvenskan",
    "Sweden - Elitettan Women",
    "Sweden - Division 1 Norra",
    "Norway - 1st Division",
    "Norway - Eliteserien",
    "Finland - Kakkonen Group A",
    "Finland - Kakkonen Group B",
    "Finland - Kakkonen Group C",
    "Finland - Ykkonen",
    "Denmark - Kvindeligaen Women",
    "England - Premier League",  # Adicione as principais ligas se aparecerem na API
    "Netherlands - Eredivisie",
    "Greece - A1",
    "Hungary - NB I",
    "Romania - Division A",
    "Poland - Ekstraklasa",
    # Inclua outras ligas conforme aparecerem!
]

ligas_escandinavo = [
    "Sweden - Allsvenskan",
    "Sweden - Superettan",
    "Sweden - Damallsvenskan",
    "Sweden - Elitettan Women",
    "Norway - Eliteserien",
    "Norway - 1st Division",
    "Finland - Ykkonen",
    "Finland - Kakkonen Group A",
    "Finland - Kakkonen Group B",
    "Finland - Kakkonen Group C"
]

ligas_norte_centro = [
    "USA - Major League Soccer",
    "USA - NPSL",
    "USA - National Womens Soccer League",
    "USA - USL League 2",
    "USA - USL League One",
    "USA - USL Super League Women",
    "USA - Women Premier Soccer League",
    "USA - MLS Next Pro League",
    "Canada - Premier League",
    "Mexico - Liga MX", # Se vier na API
    "CONCACAF - Gold Cup"
]

ligas_asia = [
    "Chinese Taipei - Professional League",
    "Japan - League Cup",
    "Japan - Nadeshiko Division 1 Women",
    "Japan - Regional League",
    "Japan - J2 League",
    "Japan - J3 League",
    "Korea Republic - K4 League",
    "South Korea - K League 1",
    "China - League Two",
    "China - Super League",
    "Champions League Asia",
    "Australia - NPL New South Wales",
    "Australia - NPL New South Wales U20",
    "Australia - NPL Victoria",
    "Australia - NPL Victoria U23",
    "Australia - NPL Queensland",
    "Australia - NPL Queensland Women",
    "Australia - Cup Qualifiers",
    "Australia - Victoria Premier League 1",
    "Australia - NPL Western Australia Women",
    "Australia - Queensland Premier League 2",
    "Australia - NPL South Australia",
    "New Zealand - Southern League",
    "New Zealand - Central League"
]

ligas_femininas = [
    "Japan - Nadeshiko Division 1 Women",
    "Australia - NPL Queensland Women",
    "Australia - NPL Western Australia Women",
    "Brazil - Brasileiro Women",
    "Brazil - Brasileiro Women A3",
    "Brazil - Brasileiro Women A2",
    "France - Division 1 Women",
    "Denmark - Kvindeligaen Women",
    "USA - National Womens Soccer League",
    "USA - Women Premier Soccer League",
    "Uruguay - Liga Femenina",
    "Colombia - Liga Women",
    "Chile - Primera Division Women",
    "Ecuador - Primera Women",
    # Adicione qualquer outra que surgir na API!
]

ligas_internacionais = [
    "International - Friendlies",
    "FIFA - World Cup Qualifiers Europe",
    "FIFA - World Cup Qualifiers CONCACAF",
    "FIFA - World Cup Qualifiers South America",
    "FIFA - World Cup Qualifiers Asia",
    "FIFA - Club World Cup",
    "UEFA - Super Cup",
    "CONCACAF - Gold Cup",
    "COSAFA - Cup",
    # Adicione outras copas relevantes!
]

# ----- /start com botões -----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)

    if chat_id not in filtros_por_chat:
        filtros_por_chat[chat_id] = {"ligas": None, "esportes": None}
        salvar_filtros()

    keyboard = [
        [InlineKeyboardButton("🇧🇷 Brasil", callback_data="brasil")],
        [InlineKeyboardButton("🇪🇺 Europa", callback_data="europa")],
        [InlineKeyboardButton("🌎 América do Sul", callback_data="americasul")],
        [InlineKeyboardButton("🌐 Todos", callback_data="todos")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    msg = (
        "👋 Bem-vindo ao Bot EV+!\n\n"
        "Escolha uma região abaixo para começar ou use os comandos disponíveis.\n"
        "Você pode digitar /ajuda a qualquer momento."
    )
    await update.message.reply_text(msg, reply_markup=reply_markup)

# ----- Botões de resposta interativa -----
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = str(query.message.chat_id)
    filtros_por_chat[chat_id] = filtros_por_chat.get(chat_id, {})

    data = query.data.lower()

    if data == "brasil":
        filtros_por_chat[chat_id] = {"ligas": ligas_brasil, "esportes": None}
        msg = "✅ Filtro ajustado para: 🇧🇷 Brasil."
    elif data == "europa":
        filtros_por_chat[chat_id] = {"ligas": ligas_europa, "esportes": None}
        msg = "✅ Filtro ajustado para: 🇪🇺 Europa."
    elif data == "americasul":
        filtros_por_chat[chat_id] = {"ligas": ligas_america_sul, "esportes": None}
        msg = "✅ Filtro ajustado para: 🌎 América do Sul."
    elif data == "todos":
        filtros_por_chat[chat_id] = {"ligas": None, "esportes": None}
        msg = "✅ Filtro removido! Você receberá alertas de todas as ligas."
    else:
        msg = "❓ Opção não reconhecida."

    salvar_filtros()
    await query.edit_message_text(text=msg)

# ----- Fallback para comandos inválidos -----
async def fallback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Comando não reconhecido. Digite /ajuda para ver as opções disponíveis.")

# ----- Filtros por região -----
async def set_brasil(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_brasil, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: 🇧🇷 Brasil.")
async def set_americasul(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_america_sul, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: América do Sul.")
async def set_europa(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_europa, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: Europa.")
async def set_escandinavo(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_escandinavo, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: Escandinávia.")
async def set_norte_centro(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_norte_centro, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: América do Norte/Centro.")
async def set_asia(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_asia, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: Ásia/Oceania.")
async def set_feminino(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_femininas, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: Futebol Feminino.")
async def set_internacionais(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": ligas_internacionais, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro ajustado para: Copas e Amistosos.")
async def set_todos(update, context): filtros_por_chat[str(update.effective_chat.id)] = {"ligas": None, "esportes": None}; salvar_filtros(); await update.message.reply_text("Filtro removido. Você receberá alertas de todas as ligas.")

# ----- Ver filtros -----
async def ver_filtros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    filtros = filtros_por_chat.get(chat_id, {})
    ligas = filtros.get("ligas")
    esportes = filtros.get("esportes")

    msg = "🎯 <b>Filtros atuais:</b>\n"
    msg += f"- Ligas: {'Todas' if not ligas else f'{len(ligas)} definidas'}\n"
    msg += f"- Esportes: {'Todos' if not esportes else ', '.join(esportes)}"
    await update.message.reply_text(msg, parse_mode="HTML")

# ----- Filtro por esportes -----
ESPORTES_VALIDOS = {
    "futebol": "Football", "tenis": "Tennis", "tênis": "Tennis",
    "basquete": "Basketball", "beisebol": "Baseball", "hockey": "Hockey",
    "mma": "MMA", "boxe": "Boxing", "volei": "Volleyball", "vôlei": "Volleyball"
}

async def set_esportes(update, context):
    chat_id = str(update.effective_chat.id)
    argumentos = context.args
    if not argumentos:
        await update.message.reply_text("❗ Use: /esportes futebol tenis basquete")
        return

    esportes = [ESPORTES_VALIDOS[arg.lower()] for arg in argumentos if arg.lower() in ESPORTES_VALIDOS]
    if not esportes:
        await update.message.reply_text("⚠️ Nenhum esporte reconhecido.")
        return

    filtros_por_chat.setdefault(chat_id, {})["esportes"] = esportes
    salvar_filtros()
    await update.message.reply_text(f"✅ Esportes configurados: {', '.join(esportes)}")

# ----- /ajuda -----
async def ajuda(update, context):
    msg = (
        "📚 Comandos disponíveis:\n\n"
        "/brasil /americasul /europa /escandinavo /nortecentro /asia /feminino /internacionais\n"
        "/todos - Remove filtros\n"
        "/esportes futebol basquete etc\n"
        "/filtros - Ver filtros atuais\n"
        "/scan - Rodar busca manual\n"
        "/ajuda - Mostrar comandos"
    )
    await update.message.reply_text(msg)

# ----- /scan manual -----
async def scan_handler(update, context):
    await update.message.reply_text("🔎 Iniciando scan manual...")
    chat_id = str(update.effective_chat.id)
    resultado = scan_apostas(chat_id)
    await update.message.reply_text(f"✅ Scan finalizado!\n{resultado}")

# ----- Inicializar bot -----
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Comandos principais
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("ajuda", ajuda))
app.add_handler(CommandHandler("scan", scan_handler))
app.add_handler(CommandHandler("filtros", ver_filtros))

# Regiões
app.add_handler(CommandHandler("brasil", set_brasil))
app.add_handler(CommandHandler("americasul", set_americasul))
app.add_handler(CommandHandler("europa", set_europa))
app.add_handler(CommandHandler("escandinavo", set_escandinavo))
app.add_handler(CommandHandler("americanortecentro", set_norte_centro))
app.add_handler(CommandHandler("asia", set_asia))
app.add_handler(CommandHandler("feminino", set_feminino))
app.add_handler(CommandHandler("internacionais", set_internacionais))
app.add_handler(CommandHandler("todos", set_todos))

# Esportes
app.add_handler(CommandHandler("esportes", set_esportes))

# Botões interativos
app.add_handler(CallbackQueryHandler(callback_handler))

# Comando inválido
app.add_handler(MessageHandler(filters.COMMAND, fallback_handler))

if __name__ == "__main__":
    app.run_polling()