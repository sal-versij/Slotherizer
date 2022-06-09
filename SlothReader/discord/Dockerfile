FROM python:3

RUN pip3 install discord discord.py python-dotenv confluent-kafka
WORKDIR /app

CMD [ "python3", "sloth_reader.py" ]