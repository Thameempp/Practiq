from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from app.core.config import settings
from app.routes.upload import router as upload_router
from app.services.generator import ask_pdf
from app.services.mcq.generator import MCQGenerationError, generate_mcqs
from app.services.mcq.schemas import MCQRequest, MCQResponse

app = FastAPI()

app.include_router(upload_router)

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


class QuestionScope(BaseModel):
    id: str | None = None
    title: str
    type: str | None = None
    documentId: str | None = None
    filename: str | None = None
    page: int | None = None
    pageLabel: str | None = None
    summary: str | None = None
    excerpt: str | None = None
    descendantTitles: list[str] = []


class QuestionRequest(BaseModel):
    question : str
    scope: QuestionScope | None = None
    document_id: str | None = None
    outline: list[str] = []


@app.post('/ask')
def ask(request: QuestionRequest):
    return StreamingResponse(
        ask_pdf(
            request.question,
            scope=request.scope.model_dump() if request.scope else None,
            document_id=request.document_id,
            outline=request.outline,
        ),
        media_type='text/plain',
        headers={
            'cache-control':'no-cache',
            'x-accel-buffering':'no'
        }
    )


@app.post('/mcq', response_model=MCQResponse)
def generate_quiz(request: MCQRequest):
    try:
        return generate_mcqs(
            document_id=request.document_id,
            scope=request.scope,
            count=request.count,
        )
    except MCQGenerationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
