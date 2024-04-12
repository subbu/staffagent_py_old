from confluent_kafka.serialization import StringSerializer
from utils.queue_utils import get_producer, delivery_report
from confluent_kafka import Producer
import datetime



class IndexingStatus():
    NOT_STARTED = "NOT STARTED"
    IN_PROGRESS = "IN PROGRESS"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class ReplyBackProducerClass:
    def __init__(self, reply_back_topic_name: str) -> None:
        self.reply_back_topic_name = reply_back_topic_name
        self.key_serializer = StringSerializer()
        self.value_serializer= StringSerializer()
        self.producer = Producer(get_producer())

    def put_to_queue(self, status: str, job_application_id: str):
        try:
            data = {
                "job_application_id" : job_application_id,
                "status" : status,
                "captured_at" : str(datetime.datetime.now())
            }
            data_to_be_sent= str(data)
            self.producer.produce(topic=self.reply_back_topic_name,
                                key=self.key_serializer(job_application_id),
                                value=self.value_serializer(data_to_be_sent),
                                on_delivery=delivery_report)
            print("Produced to QUEUE", status, " ", job_application_id)
        except:
            print("Value Error")
