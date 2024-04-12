import os
from helpers.pinecone_conn import PineconeManager
from helpers.aws_helper import download_file_from_s3
from llama_parse import LlamaParse
from helpers.pdf_chunker import chunker, to_textnodes, append_metadata
from helpers.embeddings_openai import append_embeddings
from models.models import User
from models.reply_class import ReplyBackProducerClass, IndexingStatus
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
LLAMA_INDEX_API_KEY = os.getenv("LLAMA_INDEX_API_KEY")

def process_data(user: User, reply_back_producer_instance: ReplyBackProducerClass) -> None:
    pinecone_instance = PineconeManager("resumestore", PINECONE_API_KEY)

    reply_back_producer_instance.put_to_queue(
        status=IndexingStatus.IN_PROGRESS, job_application_id=user.job_application_id)

    if download_file_from_s3(user.resume_path):
        print("File Downloaded Successfully")
    else:
        exit
    parser = LlamaParse(api_key= LLAMA_INDEX_API_KEY, result_type="text")

    parsed_url = urlparse(user.resume_path)
    object_key = parsed_url.path.lstrip('/')
    PATHTO_BLOB_URL = "uploads/" + object_key
    documents = parser.load_data(PATHTO_BLOB_URL)

    if os.path.exists(PATHTO_BLOB_URL):
        os.remove(PATHTO_BLOB_URL)
        print(f"{PATHTO_BLOB_URL} has been deleted.")
    else:
        print(f"The file {PATHTO_BLOB_URL} does not exist.")

    text_chunks, doc_idxs = chunker(documents)
    nodes = to_textnodes(documents, text_chunks, doc_idxs)
    nodes = append_metadata(nodes, user)
    nodes = append_embeddings(nodes)
    pinecone_instance.upsert_to_pinecone(nodes)

    reply_back_producer_instance.put_to_queue(
        status=IndexingStatus.SUCCESS, job_application_id=user.job_application_id)

