import asyncio
from confluent_kafka import Consumer, KafkaException, KafkaError
import signal
import logging
import os
import json
from resume.extraction import ResumeExtractor
from resume.processing import ResumeProcessor
from dotenv import load_dotenv
from staffagent_api import staff_agent_api_client

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LANGCHAIN_API_KEY = os.getenv('LANGCHAIN_API_KEY')

os.environ["LANGCHAIN_TRACING_V2"] = "True"


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


async def main():
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
                logging.info('Received message: %s' %
                             msg.value().decode('utf-8'))
                # Process message
                await process_message(msg)

                # Commit the message offset if the message is processed successfully
                consumer.commit(msg)

    except Exception as e:
        logging.error('Exception in consumer loop: %s' % e)
    finally:
        # Close down consumer to commit final offsets and clean up
        consumer.close()


async def process_message(msg):
    """
    Process incoming messages.
    """
    logging.info(f"Processing message from topic {msg.topic()}, partition {msg.partition()}, offset {msg.offset()}")
    data = json.loads(msg.value().decode('utf-8'))
    
    data_schema = data['data_table_schema']['columns']
    model_name = data.get('model_name', 'gpt-3.5-turbo')
    # model_name = data.get('model_name', 'llama2')
    fallback_model = os.getenv('FALLBACK_MODEL', 'gpt-3.5-turbo')
    timeout = data.get('timeout', 60)


    try:
        text = ResumeExtractor.extract_text_from_pdf(data['resume_path'])
        resume_processor = ResumeProcessor(OPENAI_API_KEY, data_schema)

        try:
            if model_name:
                structured_info = await asyncio.wait_for(resume_processor.process_resume(text, model_name, fallback_model), timeout=timeout)
            else:
                structured_info = await asyncio.wait_for(resume_processor.process_resume(text, fallback_model, fallback_model), timeout=timeout)
        except Exception as e:
            logging.warning(f"Error processing message with model {model_name}: {str(e)}. Retrying with fallback model.")
            structured_info = await asyncio.wait_for(resume_processor.process_resume(text, fallback_model, fallback_model), timeout=timeout)

        api_client = staff_agent_api_client
        api_client.post_data(data, structured_info)
    except asyncio.TimeoutError:
        logging.error(f"Timeout occurred after {timeout} seconds.")
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")


if __name__ == '__main__':
    asyncio.run(main())
