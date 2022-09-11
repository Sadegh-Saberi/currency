from telegram.ext import(
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    Application,
    ContextTypes,

)
from telegram import Update
from os import system

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="ری‌استارت شدن سایت \n /restart_stie" "\n"
             "ری‌استارت شدن برنامه‌ی ارز ها \n /restart_currencies" "\n"
             "افزودن ارز ها \n /add_currencies" "\n"
             "حذف ارز ها \n /remove_currencies" "\n"
             "مشاهده‌ی ارز ها \n /currencies_list" "\n"
             "اضافه کردن آیدی عددی\n /add_user_id" "\n"
             ,
        quote=True,
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
### add currencies ###
async def add_currencies(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="جهت افزودن ارز های مورد نظر لطفا نام ارز ها را در قالب یک متن به صورتی که با اینتر از یکدیگر جداشده اند ارسال کنید.\n" \
            "BTC/USDT\nETH/USDT"
    )
    return "ENTER_ADD_CURRENCIES"

async def enter_add_currencies(update:Update,context:ContextTypes.DEFAULT_TYPE):
    file_text = ""
    with open("allowed_currencies.txt","a+") as file:
        for currency in update.message.text.replace(" ","").split("\n"):
            if currency not in file.read():
                file_text += f"{currency.upper()}\n"
            else:
                await update.message.reply_text(f"ارز {currency} در لیست ارز ها قرار دارد!")
        file.write(file_text)
    await update.message.reply_text("ارز هایی که در لیست قرار نداشتند، اضافه شدند.")
    return ConversationHandler.END

### remove currencies ###

async def remove_currencies(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text="جهت حذف ارز های مورد نظر لطفا نام ارز ها را در قالب یک متن به صورتی که با اینتر از یکدیگر جداشده اند ارسال کنید. \n" \
            "BTC/USDT\nETH/USDT"
    )
    return "ENTER_REMOVE_CURRENCIES"

async def enter_remove_currencies(update:Update,context:ContextTypes.DEFAULT_TYPE):
    with open("allowed_currencies.txt","r+") as file:
        file_text = file.read()

        for currency in update.message.text.replace(" ","").split("\n"):
            if currency in file_text:
                file_text = file_text.replace(f"{currency.upper()}\n","")
            else: update.message.reply_text(f"ارز {currency} در لیست قرار ندارد!")
        file.truncate(0)
        file.seek(0)
        file.write(file_text)

    await update.message.reply_text("ارز هایی که در لیست قرار داشتند، حذف شدند.")
    return ConversationHandler.END

### currencies list ###
async def currencies_list(update:Update,context:ContextTypes.DEFAULT_TYPE):
    with open("allowed_currencies.txt","r") as file:
        await update.message.reply_text(file.read())

### add user id ###
async def add_user_id(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("لطفا آیدی عددی مورد نظر را ارسال کنید.")
    return "GET_USER_ID"

async def get_user_id(update:Update,context:ContextTypes.DEFAULT_TYPE):
    id = update.message.text.strip()
    with open("ids.txt","a+") as file:
        file.write(f"{id}\n")
        await update.message.reply_text(f"آیدی عددی {id} اضافه شد. لطفا با همان اکانت، ربات را استارت کنید.")
    return ConversationHandler.END
        

### help ###
async def help(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await start(update,context)
### --- ###
application = Application.builder().token("5664527742:AAFI0He5hcDnV6h8iZrTvLcwTP3XUXZl4oQ").build()
application.add_handler(CommandHandler("start",start))
application.add_handler(CommandHandler("restart_stie",restart_site))
application.add_handler(CommandHandler("restart_currencies",restart_currencies))
application.add_handler(CommandHandler("currencies_list",currencies_list))
application.add_handler(CommandHandler("help",help))

application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("add_currencies",add_currencies)],
    states={
        "ENTER_ADD_CURRENCIES":[MessageHandler(filters.TEXT,enter_add_currencies),]
            },
    fallbacks = {}
    ))

application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("remove_currencies",remove_currencies)],
    states={
        "ENTER_REMOVE_CURRENCIES":[MessageHandler(filters.TEXT,enter_remove_currencies),]
            },
    fallbacks = {}
    ))

application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("add_user_id",add_user_id)],
    states={
        "GET_USER_ID":[MessageHandler(filters.TEXT,get_user_id),]
            },
    fallbacks = {}
    ))
application.add_handler(MessageHandler(filters.TEXT,help))

application.run_polling()