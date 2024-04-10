from confluent_kafka.schema_registry.json_schema import JSONSerializer
from confluent_kafka.serialization import SerializationContext, MessageField, StringSerializer
from constants import REPLY_BACK_STR
from confluent_kafka.schema_registry import SchemaRegistryClient
from queue_utils import get_schema_config, reply_back_to_dictionary, get_producer, delivery_report
from confluent_kafka import Producer
from models import ReplyBack
import datetime


class IndexingStatus():
    NOT_STARTED = "NOT STARTED"
    IN_PROGRESS = "IN PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ReplyBackProducerClass:
    def __init__(self, reply_back_topic_name: str) -> None:
        self.reply_back_topic_name = reply_back_topic_name
        self.reply_back_schema_client = SchemaRegistryClient(
            get_schema_config())
        self.key_serializer = StringSerializer()
        self.value_serializer = JSONSerializer(
            REPLY_BACK_STR, self.reply_back_schema_client, reply_back_to_dictionary)
        self.producer = Producer(get_producer())

    def put_to_queue(self, status: str, id: str):
        try:
            reply_back = ReplyBack(
                id=id,
                status=status,
                captured_at=str(datetime.datetime.now()))
            self.producer.produce(topic=self.reply_back_topic_name,
                                  key=self.key_serializer(id),
                                  value=self.value_serializer(reply_back, SerializationContext(
                                      self.reply_back_topic_name, MessageField.VALUE)),
                                  on_delivery=delivery_report)
            print("Produced to QUEUE", status, " ", id)
        except:
            print("Value Error")
