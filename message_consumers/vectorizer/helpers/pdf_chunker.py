import os
from llama_index.core.node_parser import SentenceSplitter
from .data_cleaner import remove_unwanted_chars
from llama_index.core.schema import TextNode
from models.models import User
from dotenv import load_dotenv

load_dotenv()

CHUNK_SIZE = os.getenv("CHUNK_SIZE")
CHUNK_OVERLAP_SIZE = os.getenv("CHUNK_OVERLAP_SIZE")


def chunker(documents) -> tuple[list, list]:
    doc_idxs = []
    text_chunks = []
    sentence_splitter_instance = SentenceSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP_SIZE)
    # maintain relationship with source doc index, to help inject doc metadata in (3)

    for doc_idx, page in enumerate(documents):
        page_text = page.get_text()
        page_text = remove_unwanted_chars(page_text)
        cur_text_chunks = sentence_splitter_instance.split_text(page_text)
        text_chunks.extend(cur_text_chunks)
        doc_idxs.extend([doc_idx] * len(cur_text_chunks))

    return text_chunks, doc_idxs


def to_textnodes(documents, text_chunks: list, doc_idxs: list) -> list[TextNode]:
    nodes = []  # Array to store the TextNode Type of Data
    for idx, text_chunk in enumerate(text_chunks):
        node = TextNode(
            text=text_chunk,
        )
        src_doc_idx = doc_idxs[idx]
        src_page = documents[src_doc_idx]
        nodes.append(node)
    return nodes


def append_metadata(nodes: list[TextNode], user: User) -> list[TextNode]:
    metadata = {
        "job_application_id": user.job_application_id,
        "type": user.type,
        "resume_content": user.resume_content,
        "resume_path": user.resume_path,
        "captured_at": user.captured_at,
        "position_applied": user.position_applied_for
    }
    for i in range(len(nodes)):
        nodes[i].metadata = metadata
    return nodes
