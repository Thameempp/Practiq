from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from app.core.config import settings
from app.routes.upload import router as upload_router
from app.api.chat_schemas import QuestionRequest, QuestionScope
from app.api.documents import router as documents_router
from app.api.sources import router as sources_router
from app.api.verification import router as verification_router
from app.api.document_map import router as document_map_router
from app.api.lifecycle import lifespan
from app.orchestration.service import get_orchestrator
from app.orchestration.errors import OrchestrationError
from app.api.workflow_stream import response_headers, stream_workflow
from app.services.mcq.schemas import MCQRequest, MCQResponse

app = FastAPI(lifespan=lifespan)

app.include_router(upload_router)
app.include_router(documents_router)
app.include_router(sources_router)
app.include_router(verification_router)
app.include_router(document_map_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.CORS_ORIGINS),
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['Accept-Ranges', 'Content-Range', 'Content-Length', 'ETag']
)


@app.get('/health')
def health_check():
    return {"status": "ok"}


@app.get('/')
def root():
    return {"status": "ok"}


@app.post('/ask')
def ask(request: QuestionRequest, connection: Request):
    coordinator = get_orchestrator()
    try:
        run = coordinator.prepare(request)
    except OrchestrationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    if run.plan is None:
        return JSONResponse({**run.decision.response(), "request_id": run.state.request_id},
                            headers=response_headers(run))
    sse = "text/event-stream" in connection.headers.get("accept", "")
    return StreamingResponse(stream_workflow(coordinator, run, connection, sse=sse),
                             media_type="text/event-stream" if sse else "text/plain",
                             headers=response_headers(run))


@app.post('/mcq', response_model=MCQResponse)
def generate_quiz(request: MCQRequest):
    try:
        return get_orchestrator().quiz(request)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except OrchestrationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
