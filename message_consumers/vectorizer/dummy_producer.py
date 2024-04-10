import datetime
import socket
from decouple import config
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer, SerializationContext, MessageField
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer
from constants import SCHEMA_STR
from models import User
from queue_utils import user_to_dictionary, delivery_report, get_producer, get_schema_config


def main():
    topic_name = config('TOPIC_NAME', default="theonlytopic", cast=str)
    schema_client = SchemaRegistryClient(get_schema_config())
    key_serializer = StringSerializer()
    value_serializer = JSONSerializer(
        SCHEMA_STR, schema_client, user_to_dictionary)
    producer = Producer(get_producer())

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
