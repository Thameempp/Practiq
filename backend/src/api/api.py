from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from src.core.config import settings

from src.services.llm import ask_pdf

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/health')
def health_check():
    return {"status": "ok"}


@app.get('/')
def root():
    return {"status": "ok"}


class QuestionRequest(BaseModel):
    question : str


@app.post('/ask')
def ask(request: QuestionRequest):
    return StreamingResponse(
        ask_pdf(request.question),
        media_type='text/plain',
        headers={
            'cache-control':'no-cache',
            'x-accel-buffering':'no'
        }
    )