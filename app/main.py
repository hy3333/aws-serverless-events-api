from fastapi import FastAPI
from mangum import Mangum

from app.models.event import EventCreate, EventResponse
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


@app.get("/users/{user_id}/events", response_model=list[EventResponse])
def list_events(user_id: str):
    return list_events_service(user_id)


@app.get("/users/{user_id}/events/{event_id}", response_model=EventResponse)
def get_event(user_id: str, event_id: str):
    return get_event_service(user_id, event_id)


@app.get("/events/by-date/{event_date}", response_model=list[EventResponse])
def list_events_by_date(event_date: str):
    return list_events_by_date_service(event_date)


@app.delete("/users/{user_id}/events/{event_id}", status_code=204)
def delete_event(user_id: str, event_id: str):
    delete_event_service(user_id, event_id)
    return


handler = Mangum(app)