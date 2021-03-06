import os
from discord.ext import commands
import json
import re
from aiokafka import AIOKafkaConsumer
import asyncio

print("Avvio di discord")

# Configuration variable
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')
kafka_server = os.getenv("KAFKA_SERVER")

# Take the message, format it and save all in the file chatLog.json
@bot.command(name='slotherizer')
async def phrase(ctx, message_number):
    # Check if it is an integer
    if re.match(r'^\s*\d+\s*$', message_number):
        message_number = int(message_number)
        messages = await ctx.channel.history(limit=message_number, oldest_first=False).flatten()

        file = open('/usr/share/logs/chatLog.json', 'a')

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
        await ctx.send("La si prega di inserire un numero intero")


# @bot.event
# async def on_message(message):
# 	if message.content == "qual'e la risposta?":
# 		await message.channel.send("42")

# Consumer Kafka
async def consume():
    consumer = AIOKafkaConsumer(
        'send-to-discord',
        bootstrap_servers=kafka_server,
        group_id="discord-consumer")
    # Get cluster layout and join group `my-group`
    await consumer.start()
    try:
        # Consume messages
        async for msg in consumer:
            print("consumed: ", msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp)
            channel = bot.get_channel(int(msg.key))
            await channel.send(msg.value.decode("utf-8"))
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()

asyncio.get_event_loop().create_task(consume())
print("starting threads")

bot.run(TOKEN)
