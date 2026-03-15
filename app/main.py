import logging

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from mangum import Mangum

from app.models.event import EventCreate, EventResponse, PaginatedEventsResponse
from app.services.event_service import (
    create_event_service,
    get_event_service,
    list_events_service,
    list_events_by_date_service,
    delete_event_service,
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = FastAPI()


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url.path}")

    response = await call_next(request)

    logger.info(f"Response status: {response.status_code}")

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}"
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Unexpected error occurred"
        },
    )


@app.get("/")
def root():
    return {"Message": "Events API is running via CI/CD"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate):
    return create_event_service(event)


@app.get("/users/{user_id}/events", response_model=PaginatedEventsResponse)
def list_events(
    user_id: str,
    limit: int = Query(10, ge=1, le=100),
    next_token: str | None = None
):
    return list_events_service(user_id, limit, next_token)


@app.get("/users/{user_id}/events/{event_id}", response_model=EventResponse)
def get_event(user_id: str, event_id: str):
    return get_event_service(user_id, event_id)


@app.get("/events/by-date/{event_date}", response_model=PaginatedEventsResponse)
def list_events_by_date(
    event_date: str,
    limit: int = Query(10, ge=1, le=100),
    next_token: str | None = None
):
    return list_events_by_date_service(event_date, limit, next_token)


@app.delete("/users/{user_id}/events/{event_id}", status_code=204)
def delete_event(user_id: str, event_id: str):
    delete_event_service(user_id, event_id)
    return


handler = Mangum(app, api_gateway_base_path="/prod")