from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
import boto3

from app.models.event import EventCreate, EventResponse

dynamodb = boto3.resource("dynamodb", region_name="ap-south-2")
table = dynamodb.Table("EventsV2")


def create_event_service(event: EventCreate) -> EventResponse:
    if event.end_time <= event.start_time:
        raise HTTPException(
            status_code=400,
            detail="end_time must be greater than start_time"
        )

    event_id = str(uuid4())
    created_at = datetime.now(timezone.utc)

    event_date = event.start_time.date().isoformat()

    item = {
        "user_id": event.user_id,
        "event_id": event_id,
        "event_date": event_date,
        "title": event.title,
        "description": event.description,
        "start_time": event.start_time.isoformat(),
        "end_time": event.end_time.isoformat(),
        "created_at": created_at.isoformat(),
    }

    table.put_item(Item=item)

    return EventResponse(**item)


def get_event_service(user_id: str, event_id: str) -> EventResponse:
    response = table.get_item(
        Key={
            "user_id": user_id,
            "event_id": event_id
        }
    )

    item = response.get("Item")

    if item is None:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse(**item)


def list_events_service(user_id: str) -> list[EventResponse]:
    response = table.query(
        KeyConditionExpression="user_id = :uid",
        ExpressionAttributeValues={
            ":uid": user_id
        }
    )

    items = response.get("Items", [])

    return [EventResponse(**item) for item in items]


def list_events_by_date_service(event_date: str) -> list[EventResponse]:
    response = table.query(
        IndexName="EventDateIndex",
        KeyConditionExpression="event_date = :d",
        ExpressionAttributeValues={
            ":d": event_date
        }
    )

    items = response.get("Items", [])

    return [EventResponse(**item) for item in items]


def delete_event_service(user_id: str, event_id: str) -> None:
    response = table.get_item(
        Key={
            "user_id": user_id,
            "event_id": event_id
        }
    )

    item = response.get("Item")

    if item is None:
        raise HTTPException(status_code=404, detail="Event not found")

    table.delete_item(
        Key={
            "user_id": user_id,
            "event_id": event_id
        }
    )