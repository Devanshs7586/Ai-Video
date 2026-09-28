import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from core.vector_store import build_vector_store, load_vector_store, get_retriever


def get_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def _chain_from_retriever(retriever):
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an expert AI video assistant. Answer the user's question based ONLY on the transcript context below.
If the answer is not supported by the context, say: "I could not find this information in the transcript."
Be concise, precise, and clearly distinguish direct transcript information from any explanation.

Transcript context:
{context}"""),
        ("human", "{question}"),
    ])
    return (
        {"context": retriever | RunnableLambda(format_docs), "question": RunnablePassthrough()}
        | prompt
        | get_llm()
        | StrOutputParser()
    )


def build_rag_chain(transcript: str, job_id: str = "default"):
    vector_store = build_vector_store(transcript, collection_name=f"meeting_{job_id}")
    return _chain_from_retriever(get_retriever(vector_store, k=4))


def load_rag_chain(collection_name: str = "meeting_transcript"):
    vector_store = load_vector_store(collection_name=collection_name)
    return _chain_from_retriever(get_retriever(vector_store, k=4))


def ask_question(rag_chain, question: str) -> str:
    return rag_chain.invoke(question)
