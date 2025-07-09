# Hospital Directory API

This is a simple RESTful API for managing hospital information. It allows users to add, view, update, and delete hospital records. The data is stored in-memory.

## Features

- Add Hospital
- Get all Hospitals
- Get Hospital by ID
- Update Hospital
- Delete Hospital

## Tech Stack

- **Language:** Python 3.8+
- **Web Framework:** FastAPI
- **Data Persistence:** In-memory storage

## Setup and Run

Follow these steps to set up and run the application locally:

### 1. Clone the repository (if you haven't already)

```bash
git clone https://github.com/your-repo/hospital-directory-api.git
cd hospital-directory-api
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv paribus-assignment
source paribus-assignment/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
uvicorn main:app --reload
```

The API will be accessible at `http://127.0.0.1:8000`.

### 5. API Documentation

Once the application is running, you can access the interactive API documentation (Swagger UI) at:

`http://127.0.0.1:8000/docs`

## Hospital Model

Each hospital record has the following attributes:

- `id` (integer): Unique identifier
- `name` (string): Hospital name
- `address` (string): Hospital address
- `phone` (string, optional): Hospital phone number
- `created_at` (timestamp): Automatically set on creation

## Example Usage (using `curl`)

### Add a new Hospital

```bash
curl -X POST "http://127.0.0.1:8000/hospitals/" -H "Content-Type: application/json" -d '{
  "name": "General Hospital",
  "address": "123 Main St",
  "phone": "555-1234"
}'
```

### Get all Hospitals

```bash
curl -X GET "http://127.0.0.1:8000/hospitals/"
```

### Get Hospital by ID

```bash
curl -X GET "http://127.0.0.1:8000/hospitals/1"
```

### Update a Hospital

```bash
curl -X PUT "http://127.0.0.1:8000/hospitals/1" -H "Content-Type: application/json" -d '{
  "name": "General Hospital (Updated)",
  "phone": "555-5678"
}'
```

### Delete a Hospital

```bash
curl -X DELETE "http://127.0.0.1:8000/hospitals/1"
```
