from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from handlers import *
from config import BOT_TOKEN

def main():
    from database import init_db
    init_db()
    
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(confirm_delete_player, pattern="^delete_"))
    app.add_handler(CallbackQueryHandler(handle_pagination, pattern="^(prev_page|next_page|back_to_menu)$"))
    app.add_handler(CallbackQueryHandler(handle_toggle_playing, pattern="^toggle_playing_"))
    app.add_handler(MessageHandler(filters.Regex(r"^(5v5|6v6|8v8)$"), handle_generate_teams))
    
    app.run_polling()

if __name__ == "__main__":
    main()