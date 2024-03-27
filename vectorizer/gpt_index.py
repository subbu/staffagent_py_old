from pinecone_conn import PineconeManager
from decouple import config
from azure_helpers import download_from_blob_storage
from llama_parse import LlamaParse
from pdf_chunker import chunker, to_textnodes, append_metadata
from embeddings_openai import append_embeddings
from models import User
import datetime
from llama_index.core.schema import TextNode


def process_data(user: User) -> None:
    pinecone_instance = PineconeManager("resumestore", config(
        "PINECONE_API_KEY", default=None, cast=str))
    if download_from_blob_storage(user.blob_url):
        print("File Downloaded Successfully")
    else:
        exit
    parser = LlamaParse(api_key=config("LLAMA_INDEX_API_KEY",
                        default=None, cast=str), result_type="text")
    parts = user.blob_url.split('/')
    blob_name = parts[-1]
    PATHTO_BLOB_URL = "uploads/" + blob_name + ".pdf"
    documents = parser.load_data(PATHTO_BLOB_URL)
    text_chunks, doc_idxs = chunker(documents)
    nodes = to_textnodes(documents, text_chunks, doc_idxs)
    nodes = append_metadata(nodes, user)
    nodes = append_embeddings(nodes)
    # print(nodes)
    pinecone_instance.upsert_to_pinecone(nodes)


# dic = User(
#     id='d80e4e87-464a-4394-b033-13e7c4d5ca21',
#     name="Jai Anand",
#     type="pdf",
#     email="jaianand5789@gmail.com",
#     phone_number="+918923074394",
#     resume_content="Hello I am Jaianand",
#     captured_at=str(datetime.datetime.now()),
#     blob_url="https://storageforpdf.blob.core.windows.net/storageforpdf/0a8a8f3c-6975-42ac-8758-afe3d5dd4d54",
#     position_applied_for="Software Developer",
#     company_name="Google")

# print(dic)
# process_data(dic)
