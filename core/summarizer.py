from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

import os


class MeetingAnalysis(BaseModel):
    title: str = Field(description="Short professional meeting title, maximum 8 words.")
    summary: str = Field(description="Professional meeting summary in bullet points.")
    action_items: str = Field(description="Numbered list of action items with task, owner and deadline.")
    key_decisions: str = Field(description="Numbered list of key decisions made in the meeting.")
    open_questions: str = Field(description="Numbered list of unresolved questions or follow-up topics.")


_analysis_cache = {}


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=os.getenv("GEMINI_API_KEY")
    )


def analyze_transcript(transcript: str) -> MeetingAnalysis:

    if transcript in _analysis_cache:
        return _analysis_cache[transcript]

    llm = get_llm()

    structured_llm = llm.with_structured_output(MeetingAnalysis)

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are an expert meeting analyst.

Analyze the complete meeting transcript and produce:

1. A short professional title of maximum 8 words.
2. A concise professional summary in bullet points.
3. All action items. For each include:
   - Task description
   - Owner
   - Deadline if mentioned, otherwise "Not specified"
4. All key decisions made.
5. All unresolved questions or topics needing follow-up.

Do not invent information that is not present in the transcript.

If no action items exist, write:
"No action items found."

If no key decisions exist, write:
"No key decisions found."

If no unresolved questions exist, write:
"No open questions found."
"""
            ),
            ("human", "{transcript}")
        ]
    )

    chain = prompt | structured_llm

    result = chain.invoke({
        "transcript": transcript
    })

    _analysis_cache[transcript] = result

    return result


def generate_title(transcript: str) -> str:
    return analyze_transcript(transcript).title


def summarize(transcript: str) -> str:
    return analyze_transcript(transcript).summary


def generate_action_items(transcript: str) -> str:
    return analyze_transcript(transcript).action_items


def generate_key_decisions(transcript: str) -> str:
    return analyze_transcript(transcript).key_decisions


def generate_questions(transcript: str) -> str:
    return analyze_transcript(transcript).open_questions