from gpt_index import process_data
from decouple import config
from constants import SCHEMA_STR
from confluent_kafka import Consumer
from confluent_kafka.serialization import SerializationContext, MessageField
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from models import User


def dict_to_user(obj, ctx) -> User:
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
        'bootstrap.servers': config("BROKER_URL", default='127.0.0.1:19092', cast=str),
        'group.id': 'group1',  # for proto we have just one group to be looked in later stages
        'auto.offset.reset': 'latest'
    }
    return consumer_conf


def main():
    topic_name = config('TOPIC_NAME', default="theonlytopic", cast=str)
    json_deserializer = JSONDeserializer(SCHEMA_STR, from_dict=dict_to_user)
    consumer = Consumer(get_consumer())
    consumer.subscribe([topic_name])

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
            # AZURE_ACCOUNT_URI = f"DefaultEndpointsProtocol={config('DefaultEndpointsProtocol')};AccountName={config('AccountName')};AccountKey={config('AccountKey')};EndpointSuffix={config('EndpointSuffix')}"
            # print(AZURE_ACCOUNT_URI)
            process_data(user)  # process data
            print("Processed for the user with id", msg.key())
    consumer.close()


if __name__ == "__main__":
    main()


# TODO
# TODO2 -> Functionality to process TEXT, DOCS, DOCX, and resume_content (txt)
