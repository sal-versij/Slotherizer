# bot.py
import os
import random
import datetime
from discord.ext import commands
import json
from dotenv import load_dotenv
import re

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

@bot.command(name = 'riassumimi')
async def phrase(ctx, message_number):
    #Controlla se è un intero
    if re.match(r'^\s*\d+\s*$', message_number):
        message_number = int(message_number)
        messages = await ctx.channel.history(limit=message_number, oldest_first=False).flatten()
     
        file = open('messages.txt', 'w')
        for element in messages:
            # Prendo i dati che mi servono
            channel = element.channel
            author = element.author
            content = element.content

            print(channel, author, content)
            print(type(channel), type(author), type(content))

            file.write(content + "\n")    
        file.close()
    else:
        await ctx.send("METTI UN INTERO CRETINO")

# @bot.event
# async def on_message(message):
# 	if message.content == "qual'e la risposta?":
# 		await message.channel.send("42")

bot.run("OTcyMTM1NTcwMzMzNjMwNTE0.Gc7EPP.wi28PC2ryWo5WYCoGAUwg0HgMv0pEYzi6VH3j0")