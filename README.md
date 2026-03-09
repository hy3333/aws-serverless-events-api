# Serverless Events API (AWS)

A production-style serverless backend API built using AWS services and Python.  
The system allows users to create, retrieve, list, and delete events using a REST API.

The application demonstrates a modern serverless architecture used in cloud-native systems.

---

# Architecture

![Architecture Diagram](docs\API Gateway Event Flow diag.png)

Request Flow:

Client → API Gateway → Lambda → FastAPI → DynamoDB

Execution logs are automatically stored in CloudWatch.

---

# Tech Stack

Backend
- Python
- FastAPI
- Mangum (ASGI adapter for AWS Lambda)

AWS Services
- API Gateway (HTTP API)
- AWS Lambda
- DynamoDB
- IAM
- CloudWatch Logs

Infrastructure
- AWS SAM template (infra/template.yaml)

---

# Features

- Create events
- Retrieve events by ID
- List all events
- Delete events
- Serverless architecture
- DynamoDB persistence
- CloudWatch logging

---

# API Endpoints

### Create Event

POST /events

Example request:

```json
{
  "user_id": "user123",
  "title": "Team meeting",
  "description": "Project sync",
  "start_time": "2026-03-10T10:00:00",
  "end_time": "2026-03-10T11:00:00"
}