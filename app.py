from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv



import os

load_dotenv()

app = FastAPI(title="AI Audio Video Assistant")

current_session = None


class ProcessRequest(BaseModel):
    source: str
    language: str = "english"


class QuestionRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def home():
    return FileResponse("frontend/index.html")


app.mount("/static", StaticFiles(directory="frontend"), name="static")


@app.post("/api/process")
def process_video(request: ProcessRequest):
    global current_session

    if not request.source.strip():
        raise HTTPException(status_code=400, detail="Please enter a YouTube URL.")

    try:
        from main import run_pipeline
        result = run_pipeline(
            request.source.strip(),
            request.language
        )

        current_session = result

        return {
            "title": result["title"],
            "transcript": result["transcript"],
            "summary": result["summary"],
            "action_items": result["action_items"],
            "key_decisions": result["key_decisions"],
            "open_questions": result["open_questions"]
        }

    except Exception as e:
        print("Processing error:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/api/ask")
def ask(request: QuestionRequest):
    global current_session

    if current_session is None:
        raise HTTPException(
            status_code=400,
            detail="Please process a meeting first."
        )

    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Please enter a question."
        )

    try:
        from core.rag_engine import ask_question
        answer = ask_question(
            current_session["rag_chain"],
            request.question.strip()
        )

        return {
            "answer": answer
        }

    except Exception as e:
        print("Question error:", e)
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )