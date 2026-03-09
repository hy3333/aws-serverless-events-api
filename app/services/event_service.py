from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
import boto3
import logging
import json

from app.models.event import EventCreate, EventResponse


# Logger configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)


# DynamoDB connection
dynamodb = boto3.resource("dynamodb", region_name="ap-south-2")
table = dynamodb.Table("Events")


def create_event_service(event: EventCreate) -> EventResponse:

    if event.end_time <= event.start_time:
        logger.warning(json.dumps({
            "event": "create_event",
            "status": "invalid_time_range"
        }))

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

    logger.info(json.dumps({
        "event": "create_event",
        "event_id": created_event.event_id,
        "user_id": created_event.user_id,
        "status": "success"
    }))

    return created_event


def get_event_service(event_id: str) -> EventResponse:

    response = table.get_item(Key={"event_id": event_id})
    item = response.get("Item")

    if item is None:

        logger.warning(json.dumps({
            "event": "get_event",
            "event_id": event_id,
            "status": "not_found"
        }))

        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    item["start_time"] = datetime.fromisoformat(item["start_time"])
    item["end_time"] = datetime.fromisoformat(item["end_time"])
    item["created_at"] = datetime.fromisoformat(item["created_at"])

    logger.info(json.dumps({
        "event": "get_event",
        "event_id": event_id,
        "status": "success"
    }))

    return EventResponse(**item)


def list_events_service() -> list[EventResponse]:

    response = table.scan()
    items = response.get("Items", [])

    events = []

    for item in items:

        item["start_time"] = datetime.fromisoformat(item["start_time"])
        item["end_time"] = datetime.fromisoformat(item["end_time"])
        item["created_at"] = datetime.fromisoformat(item["created_at"])

        events.append(EventResponse(**item))

    logger.info(json.dumps({
        "event": "list_events",
        "count": len(events),
        "status": "success"
    }))

    return events


def delete_event_service(event_id: str) -> None:

    response = table.get_item(Key={"event_id": event_id})
    item = response.get("Item")

    if item is None:

        logger.warning(json.dumps({
            "event": "delete_event",
            "event_id": event_id,
            "status": "not_found"
        }))

        raise HTTPException(
            status_code=404,
            detail="Event not found"
        )

    table.delete_item(Key={"event_id": event_id})

    logger.info(json.dumps({
        "event": "delete_event",
        "event_id": event_id,
        "status": "deleted"
    }))