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
python -m venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
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
