from flask import Flask, request
import telebot
from telebot import types
import datetime
import requests
import json
import time
import os

# Command:
# pgirl - Price Panda Girl Token
# inusd - Convert PGIRL to USD
# ineur - Convert PGIRL to EUR

server = Flask(__name__)

TOKEN = os.getenv('BOT_TOKEN')
HEROKU_APP = os.getenv('HEROKU_APP')

bot = telebot.TeleBot(TOKEN)

LASTMESAGE = datetime.datetime.utcnow()
GC_price_usd = None
GC_price_eur = None
DATA_Market = None


def get_GC_price(cur="usd"):
    URL = f"https://api.coingecko.com/api/v3/simple/price?"
    URL = URL + f"ids=panda-girl&" \
                f"vs_currencies={cur}&" \
                f"include_market_cap=true&" \
                f"include_24hr_vol=true&" \
                f"include_24hr_change=true&" \
                f"include_last_updated_at=true"
    s = requests.session()
    r = s.get(URL)
    if r.status_code != 200:
        time.sleep(30)
        get_GC_price(cur)
    j = json.loads(r.text)

    return j.get('panda-girl')


def get_GC_data():
    global DATA_Market
    global LASTMESAGE

    if DATA_Market is None or ((datetime.datetime.utcnow() - LASTMESAGE).seconds > 20):
        URL = "https://api.coingecko.com/api/v3/coins/panda-girl?"
        URL = URL + "localization=false" + "&" \
                                           "tickers=false" + "&" \
                                                             "market_data=true" + "&" \
                                                                                  "community_data=false" + "&" \
                                                                                                           "developer_data=false" + "&" \
                                                                                                                                    "sparkline=false"
        s = requests.session()
        r = s.get(URL)
        if r.status_code != 200:
            time.sleep(30)
            get_GC_data()
        DATA_Market = json.loads(r.text)

    return DATA_Market


def get_GC_priceUSD():
    global GC_price_usd
    global LASTMESAGE

    if GC_price_usd is None or ((datetime.datetime.utcnow() - LASTMESAGE).seconds > 20):
        GC_price_usd = get_GC_price("usd")
        LASTMESAGE = datetime.datetime.utcnow()
    return GC_price_usd


def get_GC_priceEUR():
    global GC_price_eur
    global LASTMESAGE

    if GC_price_eur is None or ((datetime.datetime.utcnow() - LASTMESAGE).seconds > 20):
        GC_price_eur = get_GC_price("eur")
        LASTMESAGE = datetime.datetime.utcnow()
    return GC_price_eur


def print_info_pandaGirl():
    dicDataUSD = get_GC_priceUSD()
    dicDataEUR = get_GC_priceEUR()
    dicData = get_GC_data()

    usd = format(dicDataUSD.get('usd'), ".12f")
    eur = format(dicDataEUR.get('eur'), ".12f")
    usd_market_cap = '{:,}'.format(int(dicDataUSD.get('usd_market_cap')), ".2f")
    usd_24h_vol = '{:,}'.format(int(dicDataUSD.get('usd_24h_vol')), ".2f")
    ath = format(dicData['market_data']['ath']['usd'], ".12f")

    mesage = "🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼\n\n" + \
             "💵 Price Panda Girl : " + usd + " USD\n\n" + \
             "💶 Price Panda Girl : " + eur + " EUR\n\n" + \
             "📊 Market capitalization  : " + usd_market_cap + " USD\n\n" + \
             "💱 Volume 24 h : " + usd_24h_vol + " USD\n\n" + \
             "💹  Historical ATH : " + str(ath) + "\n\n" + \
             "🐼🐼🐼🐼🐼🐼🐼🐼🐼🐼"

    return mesage


@bot.message_handler(commands=['pgirl'])
def pgirl(message):
    txt = print_info_pandaGirl()
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("💰BUY HERE",
                                        "https://pancakeswap.finance/swap?"
                                        "outputCurrency=0x4c4da68D45F23E38ec8407272ee4f38F280263c0")
    markup.add(button)
    bot.send_message(chat_id=message.chat.id,
                     text=txt,
                     parse_mode="Markdown",
                     disable_web_page_preview=True,
                     reply_markup=markup)


@bot.message_handler(commands=['inusd'])
def in_usd(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        token = int(args[1])
        dicData = get_GC_priceUSD()
        usd = dicData.get('usd')
        suma = '{:,}'.format(token * usd, ".2f")
        txt = "Your Panda Girl Tokens Have a Сost: " + suma.__str__() + " USD 💵"
        bot.send_message(chat_id=message.chat.id,
                         text=txt,
                         parse_mode="Markdown",
                         disable_web_page_preview=True)
    else:
        bot.reply_to(message, 'Usage: /inusd <count_tokens>')


@bot.message_handler(commands=['ineur'])
def in_eur(message):
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        token = int(args[1])
        dicData = get_GC_priceEUR()
        eur = dicData.get('eur')
        suma = '{:,}'.format(token * eur, ".2f")
        txt = "Your Panda Girl Tokens Have a Сost: " + suma.__str__() + " EUR 💶"
        bot.send_message(chat_id=message.chat.id,
                         text=txt,
                         parse_mode="Markdown",
                         disable_web_page_preview=True)
    else:
        bot.reply_to(message, 'Usage: /ineur <count_tokens>')


@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()

    bot.set_webhook(url='https://' + HEROKU_APP + '.herokuapp.com/' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
