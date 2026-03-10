from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
import boto3
import logging
import json

from app.models.event import EventCreate, EventResponse, PaginatedEventsResponse


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb", region_name="ap-south-2")
table = dynamodb.Table("EventsV2")


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

    logger.info(json.dumps({
        "event": "create_event",
        "event_id": event_id,
        "user_id": event.user_id,
        "event_date": event_date,
        "status": "success"
    }))

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
        logger.warning(json.dumps({
            "event": "get_event",
            "user_id": user_id,
            "event_id": event_id,
            "status": "not_found"
        }))
        raise HTTPException(status_code=404, detail="Event not found")

    logger.info(json.dumps({
        "event": "get_event",
        "user_id": user_id,
        "event_id": event_id,
        "status": "success"
    }))

    return EventResponse(**item)


def list_events_service(
    user_id: str,
    limit: int = 10,
    last_evaluated_key: str | None = None
) -> PaginatedEventsResponse:
    query_params = {
        "KeyConditionExpression": "user_id = :uid",
        "ExpressionAttributeValues": {
            ":uid": user_id
        },
        "Limit": limit
    }

    if last_evaluated_key:
        query_params["ExclusiveStartKey"] = {
            "user_id": user_id,
            "event_id": last_evaluated_key
        }

    response = table.query(**query_params)
    items = response.get("Items", [])

    parsed_items = [EventResponse(**item) for item in items]

    next_key = None
    if "LastEvaluatedKey" in response:
        next_key = response["LastEvaluatedKey"]["event_id"]

    logger.info(json.dumps({
        "event": "list_events",
        "user_id": user_id,
        "limit": limit,
        "returned_count": len(parsed_items),
        "next_key": next_key,
        "status": "success"
    }))

    return PaginatedEventsResponse(
        items=parsed_items,
        next_key=next_key
    )


def list_events_by_date_service(event_date: str) -> list[EventResponse]:
    response = table.query(
        IndexName="EventDateIndex",
        KeyConditionExpression="event_date = :d",
        ExpressionAttributeValues={
            ":d": event_date
        }
    )

    items = response.get("Items", [])
    parsed_items = [EventResponse(**item) for item in items]

    logger.info(json.dumps({
        "event": "list_events_by_date",
        "event_date": event_date,
        "returned_count": len(parsed_items),
        "status": "success"
    }))

    return parsed_items


def delete_event_service(user_id: str, event_id: str) -> None:
    response = table.get_item(
        Key={
            "user_id": user_id,
            "event_id": event_id
        }
    )

    item = response.get("Item")

    if item is None:
        logger.warning(json.dumps({
            "event": "delete_event",
            "user_id": user_id,
            "event_id": event_id,
            "status": "not_found"
        }))
        raise HTTPException(status_code=404, detail="Event not found")

    table.delete_item(
        Key={
            "user_id": user_id,
            "event_id": event_id
        }
    )

    logger.info(json.dumps({
        "event": "delete_event",
        "user_id": user_id,
        "event_id": event_id,
        "status": "deleted"
    }))