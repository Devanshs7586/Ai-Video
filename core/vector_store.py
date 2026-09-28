from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

CHROMA_DIR = "vector_db"
COLLECTION_NAME = "meeting_transcript"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL, model_kwargs={"device": "cpu"})


def build_vector_store(transcript: str, collection_name: str = COLLECTION_NAME) -> Chroma:
    splitter = RecursiveCharacterTextSplitter(chunk_size=650, chunk_overlap=80)
    chunks = splitter.split_text(transcript)
    docs = [Document(page_content=chunk, metadata={"chunk_index": i}) for i, chunk in enumerate(chunks)]
    return Chroma.from_documents(
        documents=docs,
        embedding=get_embeddings(),
        collection_name=collection_name,
        persist_directory=CHROMA_DIR,
    )


def load_vector_store(collection_name: str = COLLECTION_NAME) -> Chroma:
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_DIR,
    )


def get_retriever(vector_store: Chroma, k: int = 4):
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
