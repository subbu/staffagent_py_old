import os
import socket
from models.models import User
import datetime
from dotenv import load_dotenv

load_dotenv()
BROKER_URL = os.getenv("BROKER_URL")

def dict_to_user(obj) -> User:
    if obj is None:
        return None

    return User(
        job_application_id=obj['job_application_id'],
        type=obj['type'] if 'type' in obj else "pdf",
        resume_content=obj['resume_content'] if 'resume_content' in obj else "",
        captured_at=str(obj['captured_at'] if 'captured_at' in obj else datetime.datetime.now()),
        resume_path=obj['resume_path'],
        position_applied_for=obj['position_applied_for'] if 'position_applied_for' in obj else "UnKnown")

def get_consumer() -> dict:
    consumer_config = {
        'bootstrap.servers': BROKER_URL,
        'group.id': "vec_group",
        'default.topic.config': {'auto.offset.reset': 'smallest'},
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # We'll commit manually
    }
    return consumer_config


def delivery_report(err: any, msg: any) -> None:
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.value(), msg.topic(), msg.partition(), msg.offset()))


def get_producer() -> dict:
    producer_conf = {
        'bootstrap.servers': BROKER_URL,
        'client.id': socket.gethostname()
    }
    return producer_conf

