from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import start, handle_message, confirm_delete_player, handle_pagination, handle_toggle_playing
from config import BOT_TOKEN
from database import init_db

def main():
    init_db()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(confirm_delete_player, pattern="^delete_"))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern="^(prev_page|next_page|back_to_menu)$"))
    app.add_handler(CallbackQueryHandler(handle_toggle_playing, pattern="^toggle_playing_"))
    
    app.run_polling()