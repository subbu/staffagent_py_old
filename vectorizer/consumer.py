import uuid
import datetime
from gpt_index import process_data
from decouple import config
from constants import SCHEMA_STR
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from models import User


def dict_to_user(obj, ctx):
    if obj is None:
        return None

    return User(
        id=obj['id'],
        name=obj['name'],
        type=obj['type'],
        email=obj['email'],
        phone_number=obj['phone_number'],
        resume_content=obj['resume_content'],
        captured_at=obj['captured_at'],
        blob_url=obj['blob_url'],
        position_applied_for=obj['position_applied_for'],
        company_name=obj['company_name'])


def get_consumer() -> Consumer:
    consumer_conf = {
        'bootstrap.servers': '127.0.0.1:19092',
        'group.id': 'group1',
        'auto.offset.reset': 'latest'
    }
    return consumer_conf


def main():
    topic_name = "theonlytopic"  # config('TOPIC_NAME', default=None, cast=str)
    json_deserializer = JSONDeserializer(SCHEMA_STR, from_dict=dict_to_user)
    consumer = Consumer(get_consumer())
    consumer.subscribe([topic_name])

    while True:
        try:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            user = json_deserializer(
                msg.value(), SerializationContext(msg.topic(), MessageField.VALUE)
            )
        except Exception as e:
            print("Exception in consumer is ", e)
            break
        else:
            # PROCESSOR
            process_data(user)
            print("Processed for the user with id", msg.key())
    consumer.close()


if __name__ == "__main__":
    main()


# TODO
# TODO1 -> Method to delete the resume once the data has been upserted to the database
# TODO2 -> Functionality to process TEXT, DOCS, DOCX, and resume_content (txt)
# TODO3 -> Modify the chunk size to check what size of chunk is best suited for the vectorizer
# TODO4 -> Maintain Paid Account for Pinecone and maintain namespace for different indexes and namespaces
# TODO5 -> For now, I dont know if the tables are being processed or not
# TODO6 -> Modify the embedding models for large3, curently using the adda02 0n 1536 dimension vectors, dont know if Pincecone supports 3072 vectors
# TODO7 -> Add try catch block, make a repo and add loggers to ensure and monitor how and what is going on
# TODO8 -> SchemaRegistryClient how it works in Elixir, then only write the producer in Elixir
