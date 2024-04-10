import os
from pinecone_conn import PineconeManager
from decouple import config
from azure_helpers import download_from_blob_storage
from llama_parse import LlamaParse
from pdf_chunker import chunker, to_textnodes, append_metadata
from embeddings_openai import append_embeddings
from models import User
from reply_class import ReplyBackProducerClass, IndexingStatus


def process_data(user: User, reply_back_producer_instance: ReplyBackProducerClass) -> None:
    pinecone_instance = PineconeManager("resumestore", config(  # store needs to be done serverless in future and different for different orgs
        "PINECONE_API_KEY", default=None, cast=str))

    reply_back_producer_instance.put_to_queue(
        status=IndexingStatus.IN_PROGRESS, id=user.id)

    if download_from_blob_storage(user.blob_url):
        print("File Downloaded Successfully")
    else:
        exit
    parser = LlamaParse(api_key=config("LLAMA_INDEX_API_KEY",
                        default=None, cast=str), result_type="text")

    parts = user.blob_url.split('/')
    blob_name = parts[-1]
    PATHTO_BLOB_URL = "uploads/" + blob_name
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
        status=IndexingStatus.SUCCESS, id=user.id)


# user = User(id='25',
#             name="Vishal_Arora.pdf",
#             type="pdf",
#             email="Vishal_Arora.pdf",
#             phone_number="+25025025",
#             resume_content=".",
#             captured_at=str(datetime.datetime.now()),
#             blob_url="https://storageforpdf.blob.core.windows.net/storageforpdf/Vishal_Arora.pdf",
#             position_applied_for="Software Developer Intern",
#             company_name="Google")
# process_data(user=user)
