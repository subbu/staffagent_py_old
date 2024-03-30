import socket
from models import User, ReplyBack
from decouple import config
from confluent_kafka.serialization import SerializationContext


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


def get_consumer() -> dict:
    consumer_conf = {
        'bootstrap.servers': config("BROKER_URL", default='127.0.0.1:19092', cast=str),
        'group.id': 'group1',  # for proto we have just one group to be looked in later stages
        'auto.offset.reset': 'latest'
    }
    return consumer_conf


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


def reply_back_to_dictionary(reply_back: ReplyBack, ctx: SerializationContext) -> dict:
    return dict(
        id=reply_back.id,
        captured_at=reply_back.captured_at,
        status=reply_back.status
    )


def delivery_report(err: any, msg: any) -> None:
    if err is not None:
        print("Delivery failed for User record {}: {}".format(msg.key(), err))
        return
    print('User record {} successfully produced to {} [{}] at offset {}'.format(
        msg.key(), msg.value(), msg.topic(), msg.partition(), msg.offset()))


def get_producer() -> dict:
    producer_conf = {
        'bootstrap.servers': config("BROKER_URL", default='127.0.0.1:19092', cast=str),
        'client.id': socket.gethostname()
    }
    return producer_conf


def get_schema_config():
    schema_registry_conf = {"url": config(
        "SCHEMA_REGISTRY_URl", default="http://localhost:8081", cast=str)}
    return schema_registry_conf
