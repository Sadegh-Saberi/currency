import asyncio
from multiprocessing import context
from threading import Thread
from telegram.ext import (
    filters,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    Application,
    ConversationHandler,
)

from telegram import (
    Update,
)
#----------------UPPROXY TOken & Channel ID & Per------------------
token = "your_bot_token"
per = 00000
channel_id = 00000
             
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=





### handler functions ###
application = Application.builder().token(token).build()

# async def update_log(update:Update,context:ContextTypes.DEFAULT_TYPE):
#     print(update)
# #Start-----------------




# Get members
# amaz=telegram.ChatMemberMember.MEMBER

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id==per:
        await update.message.reply_text(text="Ù„Ø·ÙØ§ Ø§Ø² Ù‚Ø§Ù„Ø¨ Ø¯Ø³ØªÙˆØ± Ø²ÛŒØ± Ø§Ø³ØªÙØ§Ø¯Ù‡ Ú©Ù†ÛŒØ¯.\n""/repeat <ØªØ¹Ø¯Ø§Ø¯ Ù¾ÛŒØ§Ù… Ù‡Ø§> <Ø²Ù…Ø§Ù† ØªÙˆÙ‚Ù:Ø«Ø§Ù†ÛŒÙ‡> <ØªØ¹Ø¯Ø§Ø¯ Ø¯ÙˆØ± Ø§Ø±Ø³Ø§Ù„>")
        print("Login From User Id: " + str(per))
    else:
        await update.message.reply_text("Ø´Ù…Ø§ Ù…Ø¬ÙˆØ² Ù„Ø§Ø²Ù… Ø¬Ù‡Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø±Ø¨Ø§Øª Ø±Ø§ Ù†Ø¯Ø§Ø±ÛŒØ¯.")
        print("You Dont Have Permision Id: " + str(update.message.chat_id ))





#Delete----------------------------------

async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if message.forward_from_chat.id == channel_id:
        message_id = message.forward_from_message_id
        await context.bot.delete_message(chat_id=channel_id,message_id=message_id)
        


#Repeat----------------------------------

async def get_repeat_data(update:Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id==per:
        number, wait_second, period = context.args
        context.user_data["number"] = number
        context.user_data["messages"] = list()
        context.user_data["wait_second"] = wait_second
        context.user_data["period"] = period
        await update.message.reply_text(
            text="Ø§Ø·Ù„Ø§Ø¹Ø§Øª Ø¯Ø±ÛŒØ§ÙØª Ø´Ø¯Ù†Ø¯.\n"
            f"Ù„Ø·ÙØ§ {number} Ù¾ÛŒØ§Ù… Ø®ÙˆØ¯ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯. (Ø¯Ø± Ø¨Ø§Ø²Ù‡ Ù‡Ø§ÛŒ {wait_second} Ø«Ø§Ù†ÛŒÙ‡â€ŒØ§ÛŒ Ùˆ Ø¯Ø± {period} Ø¯ÙˆØ± Ø§Ø±Ø³Ø§Ù„ Ø®ÙˆØ§Ù‡Ù†Ø¯ Ø´Ø¯.)"
    )

        return "GET_MESSAGES"
    else:
        await update.message.reply_text("Ø´Ù…Ø§ Ù…Ø¬ÙˆØ² Ù„Ø§Ø²Ù… Ø¬Ù‡Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø±Ø¨Ø§Øª Ø±Ø§ Ù†Ø¯Ø§Ø±ÛŒØ¯.")
        print("You Dont Have Permision Id: " + str(update.message.chat_id ))


#Get_MSG ----------------------------------

async def send_messages(context:ContextTypes.DEFAULT_TYPE,update:Update,messages,channel_id,period):
    for period_number in range(period):
        for message in messages:
            if message.text:
                _sent_message = await context.bot.send_message(chat_id=channel_id,text=message.text)
            elif message.photo:
                _sent_message = await context.bot.send_photo(chat_id=channel_id,photo=message.photo[-1].file_id,caption=message.caption)
            elif message.animation:
                _sent_message = await context.bot.send_animation(chat_id=channel_id,animation=message.animation.file_id,caption=message.caption)
            elif message.video:
                _sent_message = await context.bot.send_video(chat_id=channel_id,video=message.video.file_id,caption=message.caption)
            elif message.voice:
                _sent_message = await context.bot.send_voice(chat_id=channel_id,voice=message.voice.file_id,caption=message.caption)
            elif message.audio:
                _sent_message = await context.bot.send_video(chat_id=channel_id,audio=message.audio.file_id,caption=message.caption)            
            elif message.document:
                _sent_message = await context.bot.send_document(chat_id=channel_id,document=message.document.file_id,caption=message.caption)

            wait_second = int(context.user_data["wait_second"])
                        
            await asyncio.sleep(wait_second)

            if period_number != (int(period)-1):
                message_id = int(_sent_message.message_id )  
                await context.bot.delete_message(chat_id=channel_id,message_id=message_id)
        await update.message.reply_text(text=f"Ø¯ÙˆØ± {period_number+1} Ø§Ø±Ø³Ø§Ù„ Ø´Ø¯.")


async def for_message(update:Update,context:ContextTypes.DEFAULT_TYPE):
    period = int(context.user_data["period"])
    messages = context.user_data["messages"]

    await send_messages(context,update,messages,channel_id,period)

async def get_messages(update:Update,context:ContextTypes.DEFAULT_TYPE):
    context.user_data["messages"].append(update.message)
    number_of_messages = len(context.user_data["messages"])
    if len(context.user_data["messages"]) < int(context.user_data["number"]):
        await update.message.reply_text(text=f"Ù¾ÛŒØ§Ù… {number_of_messages} Ø¯Ø±ÛŒØ§ÙØª Ø´Ø¯. Ù„Ø·ÙØ§ Ù¾ÛŒØ§Ù… {number_of_messages+1} Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯.")
        return "GET_MESSAGES"        
    else:
        await update.message.reply_text(text=f"Ø¢Ø®Ø±ÛŒÙ† Ù¾ÛŒØ§Ù… (Ù¾ÛŒØ§Ù…{number_of_messages}) Ø¯Ø±ÛŒØ§ÙØª Ø´Ø¯.")

        asyncio.get_event_loop().create_task(for_message(update,context))

        

    return ConversationHandler.END
# --- #

async def change_id(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id==per:
        await update.message.reply_text(text="Ù„Ø·ÙØ§ channel Ø¢ÛŒØ¯ÛŒ Ø¬Ø¯ÛŒØ¯ Ø±Ø§ Ø§Ø±Ø³Ø§Ù„ Ú©Ù†ÛŒØ¯.")
        return "CHANNEL_ID"
    else:
        await update.message.reply_text("Ø´Ù…Ø§ Ù…Ø¬ÙˆØ² Ù„Ø§Ø²Ù… Ø¬Ù‡Øª Ø§Ø³ØªÙØ§Ø¯Ù‡ Ø§Ø² Ø±Ø¨Ø§Øª Ø±Ø§ Ù†Ø¯Ø§Ø±ÛŒØ¯.")
        print("You Dont Have Permision Id: " + str(update.message.chat_id ))

async def get_id(update:Update,context:ContextTypes.DEFAULT_TYPE):
    new_channel_id = update.message.text
    global channel_id
    try:
        channel_id = int(new_channel_id)
        await update.message.reply_text("Ú†Ù†Ù„ Ø¢ÛŒØ¯ÛŒ ØªØºÛŒÛŒØ± Ø¯Ø§Ø¯Ù‡ Ø´Ø¯.")

        return ConversationHandler.END
    except: 
        await update.message.reply_text("Ú†Ù†Ù„ Ø¢ÛŒØ¯ÛŒ ÙˆØ§Ø±Ø¯ Ø´Ø¯Ù‡ Ø§Ø´ØªØ¨Ø§Ù‡ Ø§Ø³Øª. Ø¯Ù‚Øª Ø¯Ø§Ø´ØªÙ‡ Ø¨Ø§Ø´ÛŒØ¯ Ú©Ù‡ Ú†Ù†Ù„ Ø¢ÛŒØ¯ÛŒ Ø¨Ø§ÛŒØ¯ Ø´Ø§Ù…Ù„ Ø§Ø±Ù‚Ø§Ù… Ø¨Ø§Ø´Ø¯ Ùˆ Ø¨Ø§ -100 Ø´Ø±ÙˆØ¹ Ø´Ø¯Ù‡ Ø¨Ø§Ø´Ø¯.")
        return"CHANNEL_ID"

    
# --- #


#--------------------------- Check Member IN Channel------------------------

# check_member = await application.get_chat_member(-1214166516038, message.from_user.id) if check_member.status not in ["member", "creator"]: return await message.reply("<b>some text</b>", reply_markup=builderz.as_markup())

#--------------------------- Check Member IN Channel------------------------



application.add_handler(CommandHandler("start", start))

application.add_handler(MessageHandler(filters.FORWARDED, delete_message))
application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("repeat",get_repeat_data)],
    states={
        "GET_MESSAGES":[MessageHandler(filters.ALL,get_messages)],
    },
    fallbacks=[CommandHandler("start",start)],
))


application.add_handler(ConversationHandler(
    entry_points=[CommandHandler("change",change_id)],
    states={
        "CHANNEL_ID":[MessageHandler(filters.TEXT,get_id)],
    },
    fallbacks=[CommandHandler("start",start)],
))

application.run_polling()




