from pinecone.grpc import PineconeGRPC
from llama_index.vector_stores.pinecone import PineconeVectorStore


class PineconeManager:
    def __init__(self, index_name, api_key):
        self.index_name = index_name
        self.pinecone_client = PineconeGRPC(api_key=api_key)
        self.pinecone_index = self.pinecone_client.Index(self.index_name)
        self.vector_store = PineconeVectorStore(
            pinecone_index=self.pinecone_index)

    def upsert_to_pinecone(self, nodes):
        self.vector_store.add(nodes)
