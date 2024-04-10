from confluent_kafka import Consumer, KafkaException, KafkaError
import signal
import logging
import os
import json
from resume.extraction import ResumeExtractor
from resume.processing import ResumeProcessor
from config import KAFKA_CONFIG, KAFKA_TOPIC, OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)

# Create a flag to control the shutdown process
shutdown_flag = False

def create_consumer(config):
    """Create a Kafka consumer with the specified configuration."""
    return Consumer(config)

def signal_handler(signal, frame):
    """Handle any cleanup and exit on receiving a SIGINT or SIGTERM."""
    global shutdown_flag
    logging.info("Shutdown signal received.")
    shutdown_flag = True

# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def main():
    kafka_broker_url = os.environ.get('KAFKA_BROKER_URL', 'kafka:9092')
    kafka_topic = os.environ.get('KAFKA_TOPIC', 'default_topic')
    kafka_group_id = os.environ.get('KAFKA_GROUP_ID', 'default_group')
    consumer_config = {
        'bootstrap.servers': kafka_broker_url,
        'group.id': kafka_group_id,
        'default.topic.config': {'auto.offset.reset': 'smallest'},
        'auto.offset.reset': 'earliest',
        'enable.auto.commit': False  # We'll commit manually
    }

    consumer = create_consumer(consumer_config)
    consumer.subscribe(['data_extractor'])

    try:
        while not shutdown_flag:
            msg = consumer.poll(1.0)  # Poll for messages

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # End of partition event
                    logging.info('%% %s [%d] reached end at offset %d\n' %
                                 (msg.topic(), msg.partition(), msg.offset()))
                elif msg.error():
                    raise KafkaException(msg.error())
            else:
                # Proper message
                logging.info('Received message: %s' % msg.value().decode('utf-8'))
                # Process message
                process_message(msg)

                # Commit the message offset if the message is processed successfully
                consumer.commit(msg)

    except Exception as e:
        logging.error('Exception in consumer loop: %s' % e)
    finally:
        # Close down consumer to commit final offsets and clean up
        consumer.close()

def process_message(msg):
    """
    Process incoming messages.
    """
    logging.info(f"Processing message from topic {msg.topic()}, partition {msg.partition()}, offset {msg.offset()}")
    data = json.loads(msg.value().decode('utf-8'))
    print(data['resume_path'], data['job_application_id'], data['output_format'])
    text = ResumeExtractor.extract_text_from_pdf(data['resume_path'])
    print("Extracted Text:")
    print(text)

    resume_processor = ResumeProcessor(OPENAI_API_KEY)
    structured_info = resume_processor.process_resume(text)
    print("\nStructured Information:")
    print(structured_info)

if __name__ == '__main__':
    main()
