import asyncio
import telegram
import os
import aiosqlite
database_path = "/var/www/webApp/webApp/database.sqlite"

def number_rounder(number:float) -> str:
    # if the number is not 1, 2, 3 ...
    if int(number) != number:
        # separate the number into two parts (integer part and decimal part)
        # rstrip method does not delete the zero before the point (.) sign
        integer, decimal = f"{number:.20f}".rstrip("0").split(".")
        # get the number of zeros at the beginning of the deciaml part 
        zeros = len(decimal) - len(decimal.strip("0"))
        # add rstrip method for handling numbers like this -> 1.300002 to not convert to this -> 1.300 
        return (integer+"."+decimal[:zeros+3]).rstrip("0")
    else: return str(number)


def percentage_difference(list_of_numbers:list) -> float:
    row = list_of_numbers.copy()
    while True:
        min_value, max_value = min(row), max(row)
        try:
            result = (max_value-min_value)*100/min_value
        except ZeroDivisionError:
            row.remove(min_value)
            continue
        # correct result
        if result < 200:
            break
        # delete the maximum number and try again
        else:
            row.remove(max_value)
    # return rounded result with 2 decimal place
    return {
        "min_value_index":list_of_numbers.index(min_value),
        "max_value_index":list_of_numbers.index(max_value),
        "result": round(result,2),
    }

async def telegram_message():
        bot = telegram.Bot("5193549054:AAF0ftjRutuv3LFh-i0Q_0QrII6RB73-POg")
        ids = [302546305, 1380390649]            
        async with aiosqlite.connect(database_path) as connection:
            async with connection.cursor() as cursor:
                    exchanges = ["mexc","lbank","xt","gate","phemex","coinex","bibox"]


                    query = f"""
                    SELECT [currency name],  mexc_change_percent_sign,  mexc_change_percent, {", ".join(exchanges)}, [percentage difference]
                    FROM currencies2;
                    """
                    all_data = await (await cursor.execute(query)).fetchall()
                    async with bot:
                        for currency_data in all_data:
                            try:
                                if float(currency_data[2]) >= 20 and float(currency_data[-1]) >= 5:
                                    prices_row = [float(price) if price != None else 0 for price in currency_data[3:-1]]
                                    p_difference = percentage_difference(prices_row)
                                    min_value_index, max_value_index = p_difference["min_value_index"], p_difference["max_value_index"]

                                    message =                                                  \
                                                "نام ارز:    %s\n"                             \
                                                "درصد تغییرات در ۲۴ ساعت گذشته:    %s %s\n"  \
                                                "درصد اختلاف:    %s\n"                          \
                                                "%s :    %s\n"                                  \
                                                "%s :    %s\n"                                  \
                                    % (
                                        currency_data[0].replace("_","/"),
                                        currency_data[2], currency_data[1],
                                        currency_data[-1],
                                        exchanges[min_value_index], currency_data[3+min_value_index],
                                        exchanges[max_value_index], currency_data[3+max_value_index],
                                        )
                                    for chat_id in ids:
                                        await bot.send_message(chat_id,message)
                            except TypeError: pass

if __name__ == "__main__":
    asyncio.run(telegram_message())