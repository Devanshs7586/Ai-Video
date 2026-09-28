import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


def get_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.3,
    )


def split_transcript(transcript: str) -> list:
    splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
    return splitter.split_text(transcript)


def summarize(transcript: str) -> str:
    llm = get_llm()
    map_prompt = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a video or meeting transcript concisely. Preserve important facts, names, decisions, and context."),
        ("human", "{text}"),
    ])
    map_chain = map_prompt | llm | StrOutputParser()
    chunks = split_transcript(transcript)
    chunk_summaries = [map_chain.invoke({"text": chunk}) for chunk in chunks]
    combined = "\n\n".join(chunk_summaries)

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert content analyst. Combine these partial summaries into one clear, professional final summary. Use concise bullet points and do not invent information."),
        ("human", "{text}"),
    ])
    chain = RunnablePassthrough() | RunnableLambda(lambda x: {"text": x}) | final_prompt | llm | StrOutputParser()
    return chain.invoke(combined)


def generate_title(transcript: str) -> str:
    llm = get_llm()
    chain = (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            ("system", "Based on the transcript, generate a compelling professional title of at most 8 words. Return only the title."),
            ("human", "{text}"),
        ])
        | llm
        | StrOutputParser()
    )
    return chain.invoke(transcript[:2500])
