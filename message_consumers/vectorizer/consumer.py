import os
import json
from gpt_index import process_data
from confluent_kafka import Consumer,KafkaError
from utils.queue_utils import dict_to_user, get_consumer
from models.reply_class import ReplyBackProducerClass
from dotenv import load_dotenv

load_dotenv()

TOPIC_NAME = os.getenv('TOPIC_NAME','vectorize')
REPLY_BACK_TOPIC_NAME = os.getenv('REPLY_BACK_TOPIC_NAME','reply-back-queue')
def main():
    topic_name = TOPIC_NAME
    consumer = Consumer(get_consumer())
    consumer.subscribe([topic_name])
    reply_back_producer_instance = ReplyBackProducerClass(REPLY_BACK_TOPIC_NAME)
    
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    break
        except Exception as e:
            print("Exception in consumer is ", e)
            break
        else:
            data = json.loads(msg.value())
            user = dict_to_user(data)
            process_data(user, reply_back_producer_instance)
            print("Processed for the user with id", msg.key())
            consumer.commit(msg)
    consumer.close()


if __name__ == "__main__":
    main()