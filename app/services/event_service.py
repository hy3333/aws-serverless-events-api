from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
import boto3

from app.models.event import EventCreate, EventResponse


dynamodb = boto3.resource("dynamodb", region_name="ap-south-2")
table = dynamodb.Table("Events")


def create_event_service(event: EventCreate) -> EventResponse:
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=400,
            detail="end_time must be greater than start_time"
        )

    created_event = EventResponse(
        event_id=str(uuid4()),
        user_id=event.user_id,
        title=event.title,
        description=event.description,
        start_time=event.start_time,
        end_time=event.end_time,
        created_at=datetime.now(timezone.utc)
    )

    table.put_item(
        Item={
            "event_id": created_event.event_id,
            "user_id": created_event.user_id,
            "title": created_event.title,
            "description": created_event.description,
            "start_time": created_event.start_time.isoformat(),
            "end_time": created_event.end_time.isoformat(),
            "created_at": created_event.created_at.isoformat(),
        }
    )

    return created_event


def get_event_service(event_id: str) -> EventResponse:
    response = table.get_item(Key={"event_id": event_id})
    item = response.get("Item")

    if item is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse(**item)


def list_events_service() -> list[EventResponse]:
    response = table.scan()
    items = response.get("Items", [])
    return [EventResponse(**item) for item in items]


def delete_event_service(event_id: str) -> None:
    response = table.get_item(Key={"event_id": event_id})
    item = response.get("Item")

    if item is None:
        raise HTTPException(status_code=404, detail="Event not found")

    table.delete_item(Key={"event_id": event_id})