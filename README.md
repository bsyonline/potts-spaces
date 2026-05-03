# Potts Spaces

A simple Flask application with request logging.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Local Development Setup

### 1. Clone the repository

```bash
git clone https://github.com/bsyonline/potts-spaces.git
cd potts-spaces
```

### 2. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

## Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will be available at `http://127.0.0.1:5000/`

### Expected Response

When you visit `http://127.0.0.1:5000/`, you should see:

```
Hello
```

The server will log each request path to stdout. For example, accessing the root path will log:

```
/
```

## Running Tests

Run the test suite using pytest:

```bash
pytest
```

### Running Tests with Verbose Output

```bash
pytest -v
```

### Expected Test Output

```
test_request_logging.py ..

2 passed in X.XXs
```

## Project Structure

```
.
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── test_request_logging.py   # Test suite
└── README.md                 # This file
```