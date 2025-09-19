# Hospital Directory API Documentation

This document provides detailed information about the Hospital Directory API endpoints, request/response formats, and usage examples.

## Base URL

```
http://localhost:10000
```

## Endpoints

### Health Check

Check API availability.

**URL**: `/`
**Method**: `GET`
**Rate Limit**: 100 requests/minute

**Response**:
```json
{
  "status": "OK"
}
```

### Hospitals

#### Create Hospital

Create a new hospital record.

**URL**: `/hospitals/`
**Method**: `POST`
**Rate Limit**: 30 requests/minute
**Note**: Has a 5-second processing delay

**Request Body**:
```json
{
  "name": "General Hospital",
  "address": "123 Main St",
  "phone": "555-1234",
  "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000" (optional)
}
```

**Response**:
```json
{
  "id": 1,
  "name": "General Hospital",
  "address": "123 Main St",
  "phone": "555-1234",
  "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "active": false,
  "created_at": "2023-09-20T10:30:00Z"
}
```

**Notes**:
- If `creation_batch_id` is provided, `active` will be set to `false`
- If `creation_batch_id` is omitted, `active` will be set to `true`
- Batches are limited to 20 hospitals each

#### Get All Hospitals

Get all hospitals in the system.

**URL**: `/hospitals/`
**Method**: `GET`
**Rate Limit**: 50 requests/minute

**Response**:
```json
[
  {
    "id": 1,
    "name": "General Hospital",
    "address": "123 Main St",
    "phone": "555-1234",
    "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000",
    "active": true,
    "created_at": "2023-09-20T10:30:00Z"
  },
  {
    "id": 2,
    "name": "City Medical Center",
    "address": "456 Oak Ave",
    "phone": "555-5678",
    "creation_batch_id": null,
    "active": true,
    "created_at": "2023-09-20T10:35:00Z"
  }
]
```

#### Get Hospital by ID

Get a specific hospital by ID.

**URL**: `/hospitals/{hospital_id}`
**Method**: `GET`
**Rate Limit**: 50 requests/minute

**URL Parameters**:
- `hospital_id`: Integer ID of the hospital

**Response**:
```json
{
  "id": 1,
  "name": "General Hospital",
  "address": "123 Main St",
  "phone": "555-1234",
  "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "active": true,
  "created_at": "2023-09-20T10:30:00Z"
}
```

**Error Response (404)**:
```json
{
  "detail": "Hospital not found"
}
```

#### Update Hospital

Update an existing hospital.

**URL**: `/hospitals/{hospital_id}`
**Method**: `PUT`
**Rate Limit**: 50 requests/minute

**URL Parameters**:
- `hospital_id`: Integer ID of the hospital

**Request Body** (all fields optional):
```json
{
  "name": "Updated Hospital Name",
  "address": "999 New Address",
  "phone": "555-9999"
}
```

**Response**:
```json
{
  "id": 1,
  "name": "Updated Hospital Name",
  "address": "999 New Address",
  "phone": "555-9999",
  "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000",
  "active": true,
  "created_at": "2023-09-20T10:30:00Z"
}
```

**Error Response (404)**:
```json
{
  "detail": "Hospital not found"
}
```

#### Delete Hospital

Delete a hospital by ID.

**URL**: `/hospitals/{hospital_id}`
**Method**: `DELETE`
**Rate Limit**: 50 requests/minute

**URL Parameters**:
- `hospital_id`: Integer ID of the hospital

**Response**: 204 No Content

**Error Response (404)**:
```json
{
  "detail": "Hospital not found"
}
```

### Batch Operations

#### Get Hospitals by Batch ID

Get all hospitals belonging to a specific batch.

**URL**: `/hospitals/batch/{batch_id}`
**Method**: `GET`
**Rate Limit**: 50 requests/minute

**URL Parameters**:
- `batch_id`: UUID of the batch

**Response**:
```json
[
  {
    "id": 1,
    "name": "General Hospital",
    "address": "123 Main St",
    "phone": "555-1234",
    "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000",
    "active": false,
    "created_at": "2023-09-20T10:30:00Z"
  },
  {
    "id": 2,
    "name": "City Medical Center",
    "address": "456 Oak Ave",
    "phone": "555-5678",
    "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000",
    "active": false,
    "created_at": "2023-09-20T10:35:00Z"
  }
]
```

**Error Response (404)**:
```json
{
  "detail": "No hospitals found with the specified batch ID"
}
```

#### Activate Hospitals in Batch

Activate all hospitals in a batch.

**URL**: `/hospitals/batch/{batch_id}/activate`
**Method**: `PATCH`
**Rate Limit**: 50 requests/minute

**URL Parameters**:
- `batch_id`: UUID of the batch

**Response**:
```json
{
  "activated_count": 2,
  "message": "Activated 2 hospital(s) with batch ID 550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Responses**:

404 Not Found:
```json
{
  "detail": "No hospitals found with the specified batch ID"
}
```

400 Bad Request:
```json
{
  "detail": "Cannot activate batch: one or more hospitals in the batch are already active"
}
```

#### Delete Hospitals in Batch

Delete all hospitals in a batch.

**URL**: `/hospitals/batch/{batch_id}`
**Method**: `DELETE`
**Rate Limit**: 50 requests/minute

**URL Parameters**:
- `batch_id`: UUID of the batch

**Response**:
```json
{
  "deleted_count": 2,
  "message": "Deleted 2 hospital(s) with batch ID 550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response (404)**:
```json
{
  "detail": "No hospitals found with the specified batch ID"
}
```

## Error Handling

The API uses conventional HTTP response codes to indicate success or failure:

- **200 OK**: Request succeeded
- **204 No Content**: Request succeeded with no content to return (e.g., after DELETE)
- **400 Bad Request**: Invalid request (e.g., validation error, business rule violation)
- **404 Not Found**: Requested resource not found
- **422 Unprocessable Entity**: Request validation failed (e.g., invalid format)
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

## Rate Limiting

The API implements rate limiting to prevent abuse:

| Endpoint | Rate Limit |
|----------|------------|
| Health check | 100/minute |
| Create hospital | 30/minute |
| Other endpoints | 50/minute |

When rate limits are exceeded, the API returns a 429 Too Many Requests status code.

## Constraints

- **Batch size**: Maximum 20 hospitals per batch
- **Hospital storage**: Maximum 10,000 hospitals in memory (FIFO eviction)
- **Processing delay**: Each hospital creation takes ~5 seconds

## Examples

### Creating a Hospital

```bash
curl -X POST http://localhost:10000/hospitals/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "General Hospital",
    "address": "123 Main St",
    "phone": "555-1234"
  }'
```

### Creating a Hospital in a Batch

```bash
curl -X POST http://localhost:10000/hospitals/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "General Hospital",
    "address": "123 Main St",
    "phone": "555-1234",
    "creation_batch_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

### Activating a Batch

```bash
curl -X PATCH http://localhost:10000/hospitals/batch/550e8400-e29b-41d4-a716-446655440000/activate
```

### Deleting a Batch

```bash
curl -X DELETE http://localhost:10000/hospitals/batch/550e8400-e29b-41d4-a716-446655440000
```