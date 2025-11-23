# Email QA Agentic Platform - API Documentation

## Overview

The Email QA Agentic Platform provides a RESTful API for automating email quality assurance processes. The API allows users to fetch email proofs, run QA analyses, and retrieve detailed reports.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

API endpoints do not require authentication, but you must have valid Email on Acid and OpenAI API credentials configured in your environment.

## Endpoints

### Get Email List

Fetch a list of email proofs from Email on Acid.

```
GET /emails
```

**Response**

```json
[
  {
    "id": "string",
    "name": "string",
    "created_at": "string",
    "status": "string"
  }
]
```

**Response Codes**
- `200` - Success
- `500` - Internal server error

### Get Email Details

Fetch full HTML content and metadata for a specific email.

```
GET /emails/{email_id}
```

**Path Parameters**
- `email_id` (string, required) - Unique identifier for the email

**Response**

```json
{
  "id": "string",
  "html_content": "string",
  "metadata": {
    "subject": "string",
    "preheader": "string",
    "template_name": "string",
    "locale": "string",
    "created_at": "string"
  },
  "assets": [
    {
      "type": "string",
      "url": "string",
      "alt": "string"
    }
  ]
}
```

**Response Codes**
- `200` - Success
- `404` - Email not found
- `500` - Internal server error

### Run QA Analysis

Run deterministic and agentic QA analysis on an email.

```
POST /emails/{email_id}/qa
```

**Path Parameters**
- `email_id` (string, required) - Unique identifier for the email

**Request Body**

```json
{
  "email_id": "string"
}
```

**Response**

```json
{
  "report": {
    "email_id": "string",
    "deterministic_tests": [
      {
        "test_name": "string",
        "status": "pass|fail",
        "details": "string"
      }
    ],
    "agentic_analysis": {
      "overall_status": "pass|fail|needs_review",
      "risk_score": "number",
      "risk_level": "low|medium|high",
      "compliance_analysis": {
        "issues": [
          {
            "rule": "string",
            "description": "string",
            "severity": "string"
          }
        ]
      },
      "tone_analysis": {
        "issues": [
          {
            "rule": "string",
            "description": "string",
            "severity": "string"
          }
        ]
      },
      "accessibility_analysis": {
        "issues": [
          {
            "rule": "string",
            "description": "string",
            "severity": "string"
          }
        ]
      },
      "deterministic_results": [
        {
          "test_name": "string",
          "status": "pass|fail",
          "details": "string"
        }
      ],
      "fix_suggestions": [
        {
          "type": "string",
          "issue": "string",
          "description": "string",
          "suggestion": "string",
          "priority": "string"
        }
      ],
      "top_issues": [
        {
          "type": "string",
          "test_name": "string",
          "details": "string",
          "severity": "string"
        }
      ]
    },
    "overall_status": "pass|fail|needs_review",
    "risk_score": "number",
    "generated_at": "string"
  }
}
```

**Response Codes**
- `200` - Success
- `400` - Bad request
- `500` - Internal server error

### Get Saved Report

Fetch a previously generated QA report.

```
GET /reports/{report_id}
```

**Path Parameters**
- `report_id` (string, required) - Unique identifier for the report

**Response**

```json
{
  "report_id": "string",
  "status": "string",
  "message": "string"
}
```

**Response Codes**
- `200` - Success
- `404` - Report not found
- `500` - Internal server error

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message"
}
```

## Rate Limiting

There are currently no rate limits enforced by the API, but external services (Email on Acid, OpenAI) may have their own rate limits.

## Example Usage

### Fetch Email List

```bash
curl -X GET "http://localhost:8000/api/v1/emails"
```

### Run QA Analysis

```bash
curl -X POST "http://localhost:8000/api/v1/emails/email-123/qa" \
  -H "Content-Type: application/json" \
  -d '{"email_id": "email-123"}'
```