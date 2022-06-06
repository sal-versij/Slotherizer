import os
import time
import threading
from pathlib import Path
from discord.ext import commands
import json
from dotenv import load_dotenv
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')


@bot.command(name='slotherizer')
async def phrase(ctx, message_number):
    # Controlla se è un intero
    if re.match(r'^\s*\d+\s*$', message_number):
        message_number = int(message_number)
        messages = await ctx.channel.history(limit=message_number, oldest_first=False).flatten()

        file = open(Path(__file__).parent / '../SlothReader/logstash/json/chatLog.json', 'a')

        chat_log = {
            "channel": str(ctx.channel.id),
            "author": str(ctx.author),
            "chat": []
        }

        for element in messages:
            # Prendo i dati che mi servono
            author = str(element.author)
            content = element.content
            date = str(element.created_at)

            # Mettere in un array
            message_info = {
                "author": author,
                "content": content,
                "date": date
            }

            chat_log["chat"].append(message_info)

        json_message_info = json.dumps(chat_log)

        file.write(json_message_info + "\n")
        file.close()
    else:
        await ctx.send("METTI UN INTERO CRETINO")


def directory_checker():
    directory = Path(__file__).parent / '../SlothReader/spark/summerizes/'

    for file in os.listdir(directory):
        with open(directory / file) as json_file:
            data = json.load(json_file)
            channel = bot.get_channel(data.channel)
            channel.send(data.summerize)
        os.remove(directory / file)

    threading.Timer(1, directory_checker).start()


# @bot.event
# async def on_message(message):
# 	if message.content == "qual'e la risposta?":
# 		await message.channel.send("42")

threading.Thread(target=directory_checker).start()
bot.run(TOKEN)
