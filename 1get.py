from telegram.ext import Application
import asyncio
chat_ids = [302546305]
application = Application.builder().token("5193549054:AAF0ftjRutuv3LFh-i0Q_0QrII6RB73-POg").connect_timeout(60).get_updates_read_timeout(60).build()
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())



    


