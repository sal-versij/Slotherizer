import os
import sys
import threading
from pathlib import Path
from discord.ext import commands
import json
from dotenv import load_dotenv
import re
from confluent_kafka import Consumer, KafkaException, KafkaError

print("Avvio di discord");

# def commit_completed(err, partitions):
#     if err:
#         print(str(err))
#     else:
#         print("Committed partition offsets: " + str(partitions))

# Consumer configuration
conf = {'bootstrap.servers': "kafkaserver:29092",
        'group.id': "foo",
        'auto.offset.reset': 'smallest'}
        # 'on_commit': commit_completed


consumer = Consumer(conf)


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='!')


@bot.command(name='slotherizer')
async def phrase(ctx, message_number):
    # Controlla se è un intero
    if re.match(r'^\s*\d+\s*$', message_number):
        message_number = int(message_number)
        messages = await ctx.channel.history(limit=message_number, oldest_first=False).flatten()

        file = open('/usr/share/logstash/json/chatLog.json', 'a')

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

running = True

def consume_loop(consumer, topics):
    print("start loop")
    try:
        consumer.subscribe(topics)

        while running:
            msg = consumer.poll(timeout=1.0)
            if msg is None: continue

            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    sys.stderr.write('%% %s [%d] reached end at offset %d\n' %
                                     (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                consumer.commit(asynchronous=False)
                print("#", msg.key(), ": ", msg.value())
    except Exception as e:
        print('Exception: ' + str(e))
    finally:
        # Close down consumer to commit final offsets.
        consumer.close()

def shutdown():
    running = False

# @bot.event
# async def on_message(message):
# 	if message.content == "qual'e la risposta?":
# 		await message.channel.send("42")
print("starting threads")
threading.Thread(target=consume_loop, args=[consumer, ["send-to-discord"]])
# consume_loop(consumer, ["send-to-discord"])

bot.run(TOKEN)
