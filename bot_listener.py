import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import json
from scanner import scan_apostas
from dotenv import load_dotenv

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    load_dotenv()
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Dicionário para salvar o filtro do chat
filtros_por_chat = {}

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

# ----- Função para salvar filtros em JSON -----
def salvar_filtros():
    with open("filtros_por_chat.json", "w") as f:
        json.dump(filtros_por_chat, f)

# ----- HANDLERS DE COMANDO -----
async def set_brasil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_brasil
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: Brasil.")

async def set_sul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_america_sul
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: América do Sul.")

async def set_europa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_europa
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: Europa.")

async def set_escandinavo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_escandinavo
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: Escandinávia.")

async def set_norte_centro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_norte_centro
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: América do Norte/Centro.")

async def set_asia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_asia
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: Ásia/Oceania.")

async def set_feminino(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_femininas
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: Futebol Feminino.")

async def set_internacionais(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = ligas_internacionais
    salvar_filtros()
    await update.message.reply_text("Filtro ajustado para: Copas, Mundial, Amistosos.")

async def set_todos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    filtros_por_chat[str(update.effective_chat.id)] = None
    salvar_filtros()
    await update.message.reply_text("Filtro removido! Receberá alertas de todas as ligas.")

# Handler de ajuda (opcional)
async def ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "Comandos disponíveis:\n\n"
        "/brasil - Filtro: 🇧🇷 Brasil\n"
        "/sul - Filtro: América do Sul\n"
        "/europa - Filtro: Europa\n"
        "/escandinavo - Filtro: Escandinávia\n"
        "/nortecentro - Filtro: América do Norte/Centro\n"
        "/asia - Filtro: Ásia/Oceania\n"
        "/feminino - Filtro: Futebol Feminino\n"
        "/internacionais - Filtro: Copas, Mundial, Amistosos\n"
        "/todos - Remove filtro (todas as ligas)\n"
    )
    await update.message.reply_text(msg)

async def scan_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔎 Iniciando scan manual...")
    result = scan_apostas()
    await update.message.reply_text(f"✅ Scan finalizado!\n{result}")

# Inicialização do app
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

app.add_handler(CommandHandler("brasil", set_brasil))
app.add_handler(CommandHandler("americasul", set_sul))
app.add_handler(CommandHandler("europa", set_europa))
app.add_handler(CommandHandler("escandinavo", set_escandinavo))
app.add_handler(CommandHandler("americanortecentro", set_norte_centro))
app.add_handler(CommandHandler("asia", set_asia))
app.add_handler(CommandHandler("feminino", set_feminino))
app.add_handler(CommandHandler("internacionais", set_internacionais))
app.add_handler(CommandHandler("todos", set_todos))
app.add_handler(CommandHandler("ajuda", ajuda))  # opcional
app.add_handler(CommandHandler("scan", scan_handler))

if __name__ == "__main__":
    app.run_polling()