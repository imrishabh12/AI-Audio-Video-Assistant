from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from core.vector_store import build_vector_store, load_vector_store, get_retriever

import os


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(retriever):

    llm = get_llm()

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert meeting assistant.

Answer the user's question using ONLY the meeting transcript context
provided below.

IMPORTANT:
- If the answer is present in the context, answer it directly.
- Do NOT say that the information is missing when the context contains
  relevant information.
- If the answer truly cannot be found in the context, say:
  "I could not find this information in the meeting transcript."
- Keep the answer concise and precise.

MEETING TRANSCRIPT CONTEXT:
---------------------------
{context}
---------------------------
"""
            ),
            ("human", "{question}"),
        ]
    )

    def answer_question(question):

        # Retrieve relevant transcript chunks
        docs = retriever.invoke(question)

        # Convert retrieved documents into plain text
        context = format_docs(docs)

        # Create the final prompt
        messages = prompt.format_messages(
            context=context,
            question=question
        )

        # Ask Gemini
        response = llm.invoke(messages)

        return response.content

    return answer_question


def build_rag_chain(transcript: str):

    print("Building vector Store")

    vector_store = build_vector_store(transcript)

    retriever = get_retriever(vector_store, k=4)

    return create_rag_chain(retriever)


def load_rag_chain():

    vector_store = load_vector_store()

    retriever = get_retriever(vector_store, k=4)

    return create_rag_chain(retriever)


def ask_question(rag_chain, question: str) -> str:

    print(f"Question: {question}")

    answer = rag_chain(question)

    if isinstance(answer, list):
        answer = answer[0].get("text", str(answer))

    print(f"Answer: {answer}")

    return answer