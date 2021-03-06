import wikipedia, telebot
import requests, json
import time, threading, schedule
import os
import csv
from dotenv import load_dotenv

load_dotenv()
bot = telebot.TeleBot(os.getenv('KEY'))
wikipedia.set_lang(os.getenv('LANGUE'))

def randtitle():
    randrequest=requests.post(f'https://{os.getenv("LANGUE")}.wikipedia.org/w/api.php?format=json&action=query&generator=random&grnnamespace=0&grnlimit=1')
    jsonansw = randrequest.text
    parsed = json.loads(jsonansw)
    for test in parsed['query']['pages']:
        title = parsed['query']['pages'][test]['title']
    return title

@bot.message_handler(commands=['search'])
def search(message):
    args = message.text.split()
    messages=''
    i = 0
    if len(args) > 1:
        for row in wikipedia.search(args):
            messages+=f"{i} - {row}\n"
            i+=1
        if messages:
            sent_msg = bot.reply_to(message, messages)
            bot.register_next_step_handler(sent_msg, question, args)
        else:
            bot.reply_to(message, "Nothing found")      
    else:
        bot.reply_to(message, 'Usage: /search <question>')
def question(message, args):
    id = int(message.text)
    bot.send_message(message.chat.id, wikipedia.summary(wikipedia.search(args)[id]))

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi! Use /set <seconds> to set the timer once at what time the information will be sent and /unset to remove")


def beep(chat_id) -> None:
    try:
        bot.send_message(chat_id, wikipedia.summary(randtitle()))
    except Exception:
        print("beep crashing :clown:")

@bot.message_handler(commands=['set'])
def set_timer(message):
    beep(message.chat.id)
    args = message.text.split()
    if len(args) > 1 and args[1].isdigit():
        sec = int(args[1])
        data = [message.chat.id,sec]
        schedule.every(sec).seconds.do(beep, message.chat.id).tag(message.chat.id)
        with open("data.csv", 'w', newline='') as file:
            write = csv.writer(file)
            write.writerow(data)
    else:
        bot.reply_to(message, 'Usage: /set <seconds>')
@bot.message_handler(commands=['unset'])
def unset_timer(message):
    with open('data.csv', 'rb') as file, open('data.csv', 'wb') as out:
        write = csv.writer(out)
        for row in csv.reader(file):
            if row[0] != message.chat.id:
                writer.writerow(row)
    schedule.clear(message.chat.id)


@bot.message_handler(commands=['random'])
def randomwiki(message):
    bot.reply_to(message, wikipedia.summary(randtitle()))

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, name='bot_infinity_polling', daemon=True).start()
    with open("data.csv", newline='') as file:
        rows = csv.reader(file,delimiter=',')
        for row in rows:
            bot.send_message(row[0], wikipedia.summary(randtitle()))
            schedule.every(int(row[1])).seconds.do(beep, int(row[0])).tag(int(row[1]))
    while True:
        schedule.run_pending()
        time.sleep(1)
bot.infinity_polling()
