from telegram.ext import(
    Application,
    CommandHandler,
    ContextTypes,
)
from telegram import Update
from os import system

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="""ری‌استارت شدن سایت: /restart_stie
        ری‌استارت شدن ارز ها: /restart_currencies""",
        quote=True
    )

async def restart_site(update:Update,context:ContextTypes.DEFAULT_TYPE):
    system("sudo service apache2 restart")
    await update.message.reply_text(
        text="""
        سایت ری‌استارت شد. آدرس ها:
        http://49.12.72.200/currencies
        http://49.12.72.200/currencies2
        """,
        quote=True
        )

async def restart_currencies(update:Update,context:ContextTypes.DEFAULT_TYPE):
    system("sudo systemctl restart currency_request2-py.service")
    await update.message.reply_text(
        text="برنامه‌ی آپدیت ارز ها مجددا اجرا شد."
    )

application = Application.builder().token("5664527742:AAFI0He5hcDnV6h8iZrTvLcwTP3XUXZl4oQ").build()
application.add_handler(CommandHandler("start",start))
application.add_handler(CommandHandler("restart_stie",restart_site))
application.add_handler(CommandHandler("restart_currencies",restart_currencies))

application.run_polling()