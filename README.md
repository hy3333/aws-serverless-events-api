# Serverless Events API (AWS)

A production-style serverless REST API for managing user events, built using FastAPI and deployed on AWS using a fully serverless architecture.

## Architecture

This project uses a serverless architecture deployed via AWS SAM and CloudFormation.

Main components:

* **API Gateway (HTTP API)** – Exposes REST endpoints
* **Cognito JWT Authorizer** – Secures protected endpoints
* **AWS Lambda** – Runs the FastAPI application
* **Mangum** – ASGI adapter for Lambda
* **FastAPI** – API framework
* **DynamoDB** – Stores event data
* **CloudWatch Logs** – Application logging
* **AWS SAM + CloudFormation** – Infrastructure as Code
* **GitHub + CI/CD** – Automated deployments

## Runtime Request Flow

Client → API Gateway → Cognito Authorizer → Lambda → Mangum → FastAPI → Service Layer → DynamoDB

## Deployment Flow

Developer → GitHub → GitHub Actions → AWS SAM → CloudFormation → AWS Infrastructure

## Features

* Create events
* List user events with pagination
* Get event by ID
* Query events by date
* Delete events
* JWT authentication via Cognito
* Serverless deployment with AWS SAM
* DynamoDB-backed storage
* Structured error handling
* CloudWatch logging

## API Endpoints

Public routes:

```
GET /
GET /health
```

Protected routes (JWT required):

```
POST /events
GET /users/{user_id}/events
GET /users/{user_id}/events/{event_id}
GET /events/by-date/{event_date}
DELETE /users/{user_id}/events/{event_id}
```

## Authentication

Protected routes use **Cognito JWT Authorizer**.

Clients must include an access token:

```
Authorization: Bearer <access_token>
```

Tokens are generated through the Cognito Hosted UI OAuth flow.

## Tech Stack

* Python
* FastAPI
* Mangum
* AWS Lambda
* API Gateway (HTTP API)
* Amazon Cognito
* DynamoDB
* AWS SAM
* CloudFormation
* GitHub Actions

## Project Structure

```
app/
 ├── models/
 ├── services/
 ├── main.py

infra/
 ├── template.yaml
 ├── samconfig.toml

requirements.txt
README.md
```

## Deployment

Infrastructure is deployed using AWS SAM.

```
sam build
sam deploy
```

CloudFormation manages all infrastructure resources.

## Environment

Region:

```
ap-south-2
```

DynamoDB table:

```
EventsV2
```
## Monitoring

CloudWatch dashboard monitors:

- Lambda invocations, errors, duration, and throttles
- API Gateway request count, latency, 4XX errors, and 5XX errors
- DynamoDB read/write activity

## Future Improvements

* Rate limiting
* Event update endpoint
* Request tracing
* API usage metrics
