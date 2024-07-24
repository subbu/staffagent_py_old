import os
from dotenv import load_dotenv
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP_SIZE = os.getenv("CHUNK_OVERLAP_SIZE")

def append_embeddings(nodes):
    embed_model = OpenAIEmbedding(api_key=OPENAI_API_KEY, model="text-embedding-3-large")
    llm = OpenAI(api_key=OPENAI_API_KEY, model="gpt-4o-mini")
    Settings.llm = llm
    Settings.embed_model = embed_model
    Settings.chunk_size = CHUNK_SIZE
    Settings.chunk_overlap = CHUNK_OVERLAP_SIZE
    for node in nodes:
        node_embedding = embed_model.get_text_embedding(
            node.get_content(metadata_mode="all")
        )
        node.embedding = node_embedding
    return nodes
