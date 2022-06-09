import openai
from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp

openai.organization = "org-7WfLEfgviGF6D4bJvXBk5NFf"
elastic_index = "tap"


@udf(returnType=tp.StringType())
def tldr(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        temperature=0.7,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    print('########', prompt, response["choices"][0]["text"])

    return response["choices"][0]["text"].strip()


@udf(returnType=tp.StringType())
def create_chat(chat):
    # "Chatlog:\n"+
    return "\n".join(map(lambda r: f"[{r.date}]{r.author}: {r.content}", chat)) + "\nTl;Dr:"


kafkaServer = "kafkaserver:9092"
topicIn = "chat-log"
topicDiscord = "send-to-discord"

sparkConf = SparkConf().set("spark.app.name", "sloth-reader") \
    .set("spark.executor.heartbeatInterval", "200000") \
    .set("spark.network.timeout", "300000")

sc = SparkContext.getOrCreate(conf=sparkConf)
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("WARN")

schema = tp.StructType([
    tp.StructField("channel", tp.StringType(), False),
    tp.StructField("author", tp.StringType(), False),
    tp.StructField("chat", tp.ArrayType(tp.StructType([
        tp.StructField("author", tp.StringType(), False),
        tp.StructField("content", tp.StringType(), True),
        tp.StructField("date", tp.TimestampType(), True)
    ])), True),
])

df_kafka_in = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topicIn) \
    .option("startingOffset", "earliest") \
    .load()

df_json = df_kafka_in.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.channel", "data.author", create_chat("data.chat").alias("chat")) \
    .select("channel", "author", tldr("chat").alias("chat"))

# print stream
df_json.writeStream \
    .format("console") \
    .outputMode("append") \
    .start() \
    .awaitTermination()

# Outputting list of classes to Elastic Search
df_json \
    .writeStream \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .format("es") \
    .start(elastic_index) \
    .awaitTermination()

df_json.writeStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topicDiscord) \
    .option("startingOffset", "earliest") \
    .load()
