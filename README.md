# API Tracker

## Getting Started

### Prerequisites

- Python 3.8.10
- Redis (for Celery)

### Setup

1. **Clone the repository:**

    ```bash
    git clone [https://github.com/yourusername/apitracker.git](https://github.com/altyon-get/cnext-apitracker-backend)
    cd cnext-apitracker-backend
    ```

2. **Create a virtual environment:**

    ```bash
    python3.8 -m venv venv
    source venv/bin/activate
    ```

3. **Install the requirements:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Create a `.env` file:**

    Create a `.env` file in the project root directory and add the required credentials. Example:

    ```env
    SECRET_KEY=your_secret_key
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1
    DATABASE_URL=your_database_url
    REDIS_URL=redis://localhost:6379/0
    ```

5. **Run the server:**

    ```bash
    python manage.py runserver
    ```

### File Upload

When uploading a JSON file containing API details, logs will be generated for APIs that are not added due to errors or failures. These logs help in identifying and debugging issues with the API data.

### Running Celery

To run Celery, make sure you have Redis installed on your system. You can start the Celery worker and beat scheduler using the following commands:

```bash
celery -A cnext_apitracker_backend worker --loglevel=info
celery -A cnext_apitracker_backend beat --loglevel=info
