from core.summarizer import (
    generate_action_items,
    generate_key_decisions,
    generate_questions
)


def extract_action_items(transcript: str) -> str:
    return generate_action_items(transcript)


def extract_key_decisions(transcript: str) -> str:
    return generate_key_decisions(transcript)


def extract_questions(transcript: str) -> str:
    return generate_questions(transcript)