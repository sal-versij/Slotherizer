import openai
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp
import os

# Configuration variable
openai.organization = os.getenv("ORGANIZATION")
elastic_index = os.getenv("ELASTIC_INDEX")
engine = os.getenv("ENGINE")
kafkaServer = os.getenv("KAFKA_SERVER")
topicIn = os.getenv("TOPIC_IN")
topicDiscord = os.getenv("TOPIC_DISCORD")
print(os.getenv("OPENAI_API_KEY"))

# Call to OpenAI API
@udf(returnType=tp.StringType())
def tldr(prompt):
    try:
        response = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=0.7,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response["choices"][0]["text"].strip()
    except:
        return "Sono stati richiesti troppi messaggi, riprova con un numero minore"

# Chat formatting whit date, author and content
@udf(returnType = tp.StringType())
def create_chat(chat):
    # "Chatlog:\n"+
    return "\n".join(map(lambda r: f"[{r.date}]{r.author}: {r.content}", chat)) + "\nTl;Dr:"

# Spark Configuration
sparkConf = SparkConf().set("spark.app.name", "sloth-reader") \
    .set("spark.executor.heartbeatInterval", "200000") \
    .set("spark.network.timeout", "300000")

sc = SparkContext.getOrCreate(conf=sparkConf)
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("WARN")

# Define the collection of all fields
schema = tp.StructType([
    tp.StructField("channel", tp.StringType(), False),
    tp.StructField("author", tp.StringType(), False),
    tp.StructField("chat", tp.ArrayType(tp.StructType([
        tp.StructField("author", tp.StringType(), False),
        tp.StructField("content", tp.StringType(), True),
        tp.StructField("date", tp.TimestampType(), True)
    ])), True),
])

# Subscribe to the topic and reading Kafka stream 
df_kafka_in = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topicIn) \
    .option("startingOffset", "earliest") \
    .load()

# Data Select 
df_json = df_kafka_in.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.channel", "data.author", create_chat("data.chat").alias("chat")) \
    .select("channel", "author", tldr("chat").alias("value"))

# Spark write into a Kafka topic
df_json \
    .selectExpr("channel as key", "value") \
    .writeStream \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("topic", topicDiscord) \
    .option("startingOffset", "earliest") \
    .start() \
    .awaitTermination()
