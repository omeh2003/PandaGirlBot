from flask import Flask , request
import telebot
import datetime
import requests
import json
import time
import os
server = Flask(__name__)

TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)

datetime.datetime.utcnow()

lastmessage = datetime.datetime.utcnow()


def get_GC_price():
    URL = "https://api.coingecko.com/api/v3/simple/price?ids=panda-girl&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_last_updated_at=true"

    s = requests.session()
    r = s.get(URL)
    if r.status_code != 200:
        time.sleep(30)
        get_GC_price()
    j = json.loads(r.text)
    return j.get('panda-girl')


def get_GC_data():
    URL = "https://api.coingecko.com/api/v3/coins/panda-girl?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
    s = requests.session()
    r = s.get(URL)
    if r.status_code != 200:
        time.sleep(30)
        get_GC_price()
    j = json.loads(r.text)
    return j


def print_info_pandaGirl():
    dicData = get_GC_price()
    usd = format(dicData.get('usd'), ".12f")
    # print("Курс Panda Girl - " + usd + " USD")
    usd_market_cap = format(dicData.get('usd_market_cap'), ".2f")
    # print("Рыночная капитализация  - " + usd_market_cap + " USD")
    usd_24h_vol = format(dicData.get('usd_24h_vol'), ".2f")
    usd_24h_change = format(dicData.get('usd_24h_change'), ".2f")
    # print("Обьем торгов за 24 часа - " + usd_24h_vol + " USD")
    # print("Изменение обьема торгов в процентах - " + usd_24h_change + " %")
    dicData = get_GC_data()
    market_cap_rank = dicData['market_data']['market_cap_rank']
    ath = format(dicData['market_data']['ath']['usd'], ".12f")
    atl = format(dicData['market_data']['atl']['usd'], ".12f")
    ath_change_percentage = format(dicData['market_data']['ath_change_percentage']['usd'], ".2f")
    atl_change_percentage = format(dicData['market_data']['atl_change_percentage']['usd'], ".2f")
    total_supply = format(dicData['market_data']['total_supply'], ".2f")
    circulating_supply = format(dicData['market_data']['circulating_supply'], ".2f")
    # print("Маркет кап ранг  - " + str(market_cap_rank))
    # print("Исторический ATH - " + str(ath))
    # print("Исторический ATL  - " + atl.__str__())
    # print("от ATH  в процентах - " + ath_change_percentage.__str__())
    # print("от ATL  в процентах - " + atl_change_percentage.__str__())
    # print("Всего было выпушено монет - " + total_supply.__str__())
    # print("Монет в обращение - " + circulating_supply.__str__())
    mesage = "Price Panda Girl - " + usd + " USD\n" + \
             "Market capitalization  - " + usd_market_cap + " USD\n" + \
             "Volume 24 часа - " + usd_24h_vol + " USD\n" + \
             "Volume % - " + usd_24h_change + " %\n" + \
             "Market cap rang  - " + str(market_cap_rank) + "\n" + \
             "Historical ATH - " + str(ath) + "\n" + \
             "Historical ATL  - " + atl.__str__() + "\n" + \
             "From ATH  % - " + ath_change_percentage.__str__() + "\n" + \
             "From ATL  % - " + atl_change_percentage.__str__() + "\n" + \
             "Total supply - " + total_supply.__str__() + "\n" + \
             "Circulating suplay - " + circulating_supply.__str__() + "\n"
    return mesage


@bot.message_handler(commands=['pgirl'])
def get_text_messages(message):
    global lastmessage

    if (datetime.datetime.utcnow() - lastmessage).seconds > 10:
        txt = print_info_pandaGirl()
        bot.send_message(chat_id=-1001685153775, text=txt)
        lastmessage = datetime.datetime.utcnow()


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://pandagirl-bot.herokuapp.com/' + TOKEN)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

