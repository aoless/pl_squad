from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from pl_squad.agents.football_agent import answer_football_question

app = FastAPI()


class Question(BaseModel):
    question: str


@app.post("/api/ask")
async def ask(question: Question):
    answer = answer_football_question(question.question)
    return {"answer": answer}


app.mount("/", StaticFiles(directory="pl_squad/web/static", html=True), name="static")
