from gpt_index import process_data
from decouple import config
from constants import SCHEMA_STR
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from queue_utils import dict_to_user, get_consumer
from reply_class import ReplyBackProducerClass


def main():
    topic_name = config('TOPIC_NAME', default="theonlytopic", cast=str)
    json_deserializer = JSONDeserializer(SCHEMA_STR, from_dict=dict_to_user)
    consumer = Consumer(get_consumer())
    consumer.subscribe([topic_name])

    reply_back_producer_instance = ReplyBackProducerClass(
        "reply-back-queue")
    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            user = json_deserializer(msg.value(), SerializationContext(
                msg.topic(), MessageField.VALUE))
        except Exception as e:
            print("Exception in consumer is ", e)
            break
        else:
            process_data(user, reply_back_producer_instance)
            print("Processed for the user with id", msg.key())
    consumer.close()


if __name__ == "__main__":
    main()


# TODO
# TODO2 -> Functionality to process TEXT, DOCS, DOCX, and resume_content (txt)
# TODO3 -> Hit an api to populate the type of embedding model to use, CHUNK SIZE, CHUNK OVERLAP, GPT MODEL, VECTOR DIMNS
