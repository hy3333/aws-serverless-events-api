from fastapi import FastAPI
from mangum import Mangum

from app.models.event import EventCreate, EventResponse
from app.services.event_service import (
    create_event_service,
    get_event_service,
    list_events_service,
    delete_event_service,
)

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Events API is running"}


@app.post("/events", response_model=EventResponse, status_code=201)
def create_event(event: EventCreate):
    return create_event_service(event)


@app.get("/events/{event_id}", response_model=EventResponse)
def get_event(event_id: str):
    return get_event_service(event_id)


@app.get("/events", response_model=list[EventResponse])
def list_events():
    return list_events_service()


@app.delete("/events/{event_id}", status_code=204)
def delete_event(event_id: str):
    delete_event_service(event_id)
    return


@app.get("/health")
def health():
    return {"status": "ok"}

handler = Mangum(app)
