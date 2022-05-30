# from numpy import result_type
# from pyspark.sql.functions import udf

from pyspark import SparkContext
from pyspark.conf import SparkConf
from pyspark.sql.session import SparkSession

# from elasticsearch import Elasticsearch
from pyspark.sql.functions import from_json
import pyspark.sql.types as tp

# import time
# # making the post request to get the last prediction
# # plotting the last tag, bbox and percentage prediction
# # sending back the modified image to the telegram user
# import matplotlib.pyplot as plt
# from matplotlib.patches import Rectangle
# from PIL import Image
# import requests
# import json
# import random

kafkaServer = "kafkaserver:9092"
topic = "chat_log"

sparkConf = SparkConf().set("spark.app.name", "sloth-reader") \
    .set("spark.executor.heartbeatInterval", "200000") \
    .set("spark.network.timeout", "300000")

sc = SparkContext.getOrCreate(conf=sparkConf)
spark = SparkSession(sc)
spark.sparkContext.setLogLevel("WARN")

schema = tp.StructType([
    tp.StructField("channel", tp.IntegerType(), False),
    tp.StructField("chat", tp.ArrayType(tp.StructType([
        tp.StructField("author", tp.StringType(), False),
        tp.StructField("content", tp.StringType(), True),
        tp.StructField("date", tp.DateType(), True)
    ])), True),
])

df_kafka = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafkaServer) \
    .option("subscribe", topic) \
    .option("startingOffset", "earliest") \
    .load()

df_json = df_kafka.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", schema).alias("data")) \
    .select("data.*")

# print stream
df_json.writeStream \
    .format("console") \
    .outputMode("append") \
    .start() \
    .awaitTermination()
