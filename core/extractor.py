import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


def get_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.2,
    )


def build_chain(system_prompt: str):
    llm = get_llm()
    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([("system", system_prompt), ("human", "{text}")])
        | llm
        | StrOutputParser()
    )


def extract_action_items(transcript: str) -> str:
    return build_chain(
        "Extract all concrete action items from this transcript. For each include task, owner if known, and deadline if mentioned. "
        "Use a numbered list. If no action items exist, say 'No action items found.' Never invent owners or deadlines."
    ).invoke(transcript)


def extract_key_decisions(transcript: str) -> str:
    return build_chain(
        "Extract the key decisions or firm conclusions from this transcript. Use a numbered list. "
        "If none are present, say 'No key decisions found.' Do not infer decisions that were not actually made."
    ).invoke(transcript)


def extract_questions(transcript: str) -> str:
    return build_chain(
        "Extract unresolved questions, uncertainties, or topics explicitly needing follow-up from this transcript. "
        "Use a numbered list. If none exist, say 'No open questions found.'"
    ).invoke(transcript)
