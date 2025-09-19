# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Development server with auto-reload
uvicorn main:app --reload

# Production server (uses PORT environment variable, defaults to 10000)
python main.py

# Docker build and run
docker build -t hospital-directory .
docker run -p 10000:10000 hospital-directory
```

### API Documentation
- Interactive docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/

## Architecture Overview

This is a FastAPI-based REST API for hospital directory management with in-memory storage:

### Core Components
- **main.py**: FastAPI application with REST endpoints
- **models.py**: Pydantic models for data validation (Hospital, HospitalCreate, HospitalUpdate)
- **database.py**: In-memory data storage layer with CRUD operations

### Data Flow
1. API requests hit FastAPI endpoints in main.py
2. Pydantic models validate request/response data
3. Database module manages in-memory storage using Python lists
4. Auto-incrementing IDs managed globally in database.py

### Key Design Patterns
- **Repository Pattern**: database.py abstracts data operations
- **DTO Pattern**: Separate models for create, update, and response operations
- **Global State**: Uses module-level variables for in-memory storage (hospitals_db, next_id)

### Dependencies
- FastAPI 0.111.0: Web framework
- Uvicorn 0.30.1: ASGI server
- Pydantic 2.7.4: Data validation

## Notes
- Data persistence is in-memory only (resets on restart)
- No authentication or authorization implemented
- Uses global variables for data storage - not thread-safe for high concurrency
- Docker image targets linux/amd64 platform