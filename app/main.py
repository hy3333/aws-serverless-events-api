from fastapi import FastAPI, Query
from mangum import Mangum

from app.models.event import EventCreate, EventResponse, PaginatedEventsResponse
from app.services.event_service import (
    create_event_service,
    get_event_service,
    list_events_service,
    list_events_by_date_service,
    delete_event_service,
)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Events API is running via CI/CD"}


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
    last_evaluated_key: str | None = None
):
    return list_events_service(user_id, limit, last_evaluated_key)


@app.get("/users/{user_id}/events/{event_id}", response_model=EventResponse)
def get_event(user_id: str, event_id: str):
    return get_event_service(user_id, event_id)


@app.get("/events/by-date/{event_date}", response_model=PaginatedEventsResponse)
def list_events_by_date(
    event_date: str,
    limit: int = Query(10, ge=1, le=100),
    last_start_time: str | None = None
):
    return list_events_by_date_service(event_date, limit, last_start_time)


@app.delete("/users/{user_id}/events/{event_id}", status_code=204)
def delete_event(user_id: str, event_id: str):
    delete_event_service(user_id, event_id)
    return


handler = Mangum(app)