import os
import json
import datetime
from confluent_kafka import Producer
from confluent_kafka.serialization import StringSerializer
from models.models import User
from utils.queue_utils import delivery_report, get_producer
from dotenv import load_dotenv

load_dotenv()
TOPIC_NAME = os.getenv('TOPIC_NAME','vectorize')

def main():
    topic_name = TOPIC_NAME
    key_serializer = StringSerializer()
    value_serializer = StringSerializer()
    producer = Producer(get_producer())

    try:
        user = User(job_application_id='25',
                    type="pdf",
                    resume_content=".",
                    captured_at=str(datetime.datetime.now()),
                    resume_path="s3://staffagent-dev-resumes/ShreyaSingh_Resume.pdf",
                    position_applied_for="Software Developer Intern")
        user_json = json.dumps(user.__dict__)
        producer.produce(topic=topic_name,
                         key=key_serializer(user.job_application_id),
                         value=value_serializer(user_json),
                         on_delivery=delivery_report)
    except ValueError:
        print("Value Error")
    producer.flush()


if __name__ == "__main__":
    main()
