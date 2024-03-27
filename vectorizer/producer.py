import uuid
import datetime
import socket
from decouple import config
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from constants import SCHEMA_STR
from models import User


def user_to_dictionary(user: User, ctx: SerializationContext) -> dict:
    return dict(
        id=user.id,
        name=user.name,
        type=user.type,
        email=user.email,
        phone_number=user.phone_number,
        resume_content=user.resume_content,
        captured_at=user.captured_at,
        blob_url=user.blob_url,
        position_applied_for=user.position_applied_for,
        company_name=user.company_name
    )


def delivery_report(err: any, msg: any):
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.value(), msg.topic(), msg.partition(), msg.offset()))


def get_schema_config() -> SchemaRegistryClient:
    schema_registry_conf = {"url": "http://localhost:8081"}
    return schema_registry_conf


def get_producer() -> Producer:
    producer = Producer({
        'bootstrap.servers': '127.0.0.1:19092',
        'client.id': socket.gethostname()
    }
    )
    return producer


def main():
    topic_name = "theonlytopic"  # config('TOPIC_NAME', cast=str)
    # num_partitions = config('NUM_PARTITIONS', default=1, cast=int)
    # broker_address = config('BROKER_URL', cast=str)
    schema_client = SchemaRegistryClient(get_schema_config())
    key_serializer = StringSerializer()
    value_serializer = JSONSerializer(
        SCHEMA_STR, schema_client, user_to_dictionary)
    producer = get_producer()

    # while True :
    try:
        user = User(id='25',
                    name="Vishal_Arora.pdf",
                    type="pdf",
                    email="Vishal_Arora.pdf",
                    phone_number="+25025025",
                    resume_content=".",
                    captured_at=str(datetime.datetime.now()),
                    blob_url="https://storageforpdf.blob.core.windows.net/storageforpdf/Vishal_Arora.pdf",
                    position_applied_for="Software Developer Intern",
                    company_name="Google")
        producer.produce(topic=topic_name,
                         key=key_serializer(user.id),
                         value=value_serializer(user, SerializationContext(
                             topic_name, MessageField.VALUE)),
                         on_delivery=delivery_report)
    except ValueError:
        print("Value Error")
    producer.flush()


if __name__ == "__main__":
    main()
