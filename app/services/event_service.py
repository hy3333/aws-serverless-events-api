from uuid import uuid4
from datetime import datetime, timezone
from fastapi import HTTPException
import boto3
import logging
import json
import base64
import os

from app.models.event import EventCreate, EventResponse, PaginatedEventsResponse


logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get("EVENTS_TABLE_NAME", "EventsV2")

# Use current region from Lambda environment, not hardcoded
session = boto3.Session()
region = session.region_name or os.environ.get("AWS_REGION", "ap-south-2")
dynamodb = boto3.resource("dynamodb", region_name=region)
table = dynamodb.Table(TABLE_NAME)


def encode_token(data: dict) -> str:
    json_str = json.dumps(data)
    return base64.urlsafe_b64encode(json_str.encode()).decode()


def decode_token(token: str) -> dict:
    json_str = base64.urlsafe_b64decode(token.encode()).decode()
    return json.loads(json_str)


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
    next_token: str | None = None
) -> PaginatedEventsResponse:
    query_params = {
        "KeyConditionExpression": "user_id = :uid",
        "ExpressionAttributeValues": {
            ":uid": user_id
        },
        "Limit": limit
    }

    if next_token:
        decoded = decode_token(next_token)
        query_params["ExclusiveStartKey"] = {
            "user_id": decoded["user_id"],
            "event_id": decoded["event_id"]
        }

    response = table.query(**query_params)
    items = response.get("Items", [])

    parsed_items = [EventResponse(**item) for item in items]

    new_next_token = None
    if "LastEvaluatedKey" in response:
        new_next_token = encode_token({
            "user_id": response["LastEvaluatedKey"]["user_id"],
            "event_id": response["LastEvaluatedKey"]["event_id"]
        })

    logger.info(json.dumps({
        "event": "list_events",
        "user_id": user_id,
        "limit": limit,
        "returned_count": len(parsed_items),
        "has_next_token": new_next_token is not None,
        "status": "success"
    }))

    return PaginatedEventsResponse(
        items=parsed_items,
        next_token=new_next_token
    )


def list_events_by_date_service(
    event_date: str,
    limit: int = 10,
    next_token: str | None = None
) -> PaginatedEventsResponse:
    query_params = {
        "IndexName": "EventDateIndex",
        "KeyConditionExpression": "event_date = :d",
        "ExpressionAttributeValues": {
            ":d": event_date
        },
        "Limit": limit
    }

    if next_token:
        decoded = decode_token(next_token)
        query_params["ExclusiveStartKey"] = {
            "user_id": decoded["user_id"],
            "event_id": decoded["event_id"],
            "event_date": decoded["event_date"],
            "start_time": decoded["start_time"]
        }

    response = table.query(**query_params)
    items = response.get("Items", [])

    parsed_items = [EventResponse(**item) for item in items]

    new_next_token = None
    if "LastEvaluatedKey" in response:
        lek = response["LastEvaluatedKey"]
        new_next_token = encode_token({
            "user_id": lek["user_id"],
            "event_id": lek["event_id"],
            "event_date": lek["event_date"],
            "start_time": lek["start_time"]
        })

    logger.info(json.dumps({
        "event": "list_events_by_date",
        "event_date": event_date,
        "limit": limit,
        "returned_count": len(parsed_items),
        "has_next_token": new_next_token is not None,
        "status": "success"
    }))

    return PaginatedEventsResponse(
        items=parsed_items,
        next_token=new_next_token
    )


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