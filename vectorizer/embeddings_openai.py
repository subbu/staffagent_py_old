from decouple import config
from llama_index.core.settings import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from constants import CHUNK_OVERLAP_SIZE, CHUNK_SIZE
# MODEL	~ PAGES PER DOLLAR	PERFORMANCE ON MTEB EVAL	MAX INPUT
# text-embedding-3-small	62,500	62.3%	8191
# text-embedding-3-large	9,615	64.6%	8191
# text-embedding-ada-002	12,500	61.0%	8191


def append_embeddings(nodes):
    embed_model = OpenAIEmbedding(
        api_key=config("OPENAI_API_KEY", cast=str), model="text-embedding-3-large")
    llm = OpenAI(api_key=config("OPENAI_API_KEY", cast=str),
                 model="gpt-3.5-turbo-0125")
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
