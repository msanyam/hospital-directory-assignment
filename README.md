# Hospital Directory API

A RESTful API for managing hospital directory information with batch processing capabilities.

## Project Structure

```
hospital-directory-assignment/
├── app/                          # Main application code
│   ├── __init__.py
│   ├── main.py                   # FastAPI app and endpoints
│   ├── models.py                 # Pydantic models
│   ├── database.py               # Database operations
│   └── config.py                 # Configuration settings
├── tests/                        # Test files
│   ├── __init__.py
│   ├── conftest.py               # Test fixtures
│   ├── test_api.py               # API tests
│   ├── test_batch.py             # Batch processing tests
│   ├── test_database.py          # Database tests
│   ├── test_edge_cases.py        # Edge case tests
│   └── test_models.py            # Model tests
├── docs/                         # Documentation
│   ├── API.md                    # API documentation
│   ├── Hospital_Directory_Assignment.md
│   ├── Senior_Python_Developer_Assignment.md
│   └── TESTING.md                # Testing documentation
├── scripts/                      # Utility scripts
│   ├── run_tests.py              # Test runner
│   └── docker_push.sh            # Docker build/push script
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Docker configuration
└── pytest.ini                    # Pytest configuration
```

## Features

- **Hospital Management**: CRUD operations for hospital records
- **Batch Processing**: Group hospitals in batches for bulk operations
- **Rate Limiting**: Configurable rate limits for API endpoints
- **FIFO Storage**: In-memory storage with FIFO eviction policy (max 10,000 hospitals)
- **Validation**: Comprehensive data validation

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd hospital-directory-assignment
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Run the Application

```bash
uvicorn app.main:app --reload
```

Access the API at http://127.0.0.1:8000/ and API documentation at http://127.0.0.1:8000/docs

### Production Deployment

```bash
python -m app.main
```

The application will run on port 10000 by default (configurable via PORT environment variable).

### Docker Deployment

```bash
docker build -t hospital-directory .
docker run -p 10000:10000 hospital-directory
```

## API Documentation

See [API Documentation](docs/API.md) for detailed API endpoints and examples.

### Key Endpoints

- `GET /` - Health check
- `POST /hospitals/` - Create hospital
- `GET /hospitals/` - Get all hospitals
- `GET /hospitals/{hospital_id}` - Get hospital by ID
- `PUT /hospitals/{hospital_id}` - Update hospital
- `DELETE /hospitals/{hospital_id}` - Delete hospital
- `GET /hospitals/batch/{batch_id}` - Get hospitals by batch ID
- `PATCH /hospitals/batch/{batch_id}/activate` - Activate hospitals in batch
- `DELETE /hospitals/batch/{batch_id}` - Delete hospitals in batch

## Testing

### Run Tests

```bash
python -m pytest
```

### Run Specific Test Categories

```bash
python scripts/run_tests.py --category models
python scripts/run_tests.py --category api
python scripts/run_tests.py --category batch
```

### Run with Coverage

```bash
python scripts/run_tests.py --coverage
```

See [Testing Documentation](docs/TESTING.md) for more details on the test suite.

## Configuration

Configuration settings are centralized in `app/config.py`. Key settings include:

- `MAX_BATCH_SIZE`: Maximum hospitals in a batch (default: 20)
- `MAX_TOTAL_HOSPITALS`: Maximum total hospitals in storage (default: 10000)
- `SLOW_TASK_DELAY_SECONDS`: Processing delay in seconds (default: 5)
- Rate limits for different endpoints

## License

This project is for educational purposes only.
