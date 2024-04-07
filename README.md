# Course Capsule README.md 

## Setup Instructions
1. Clone the repository: `git clone git@github.com:CSCI375-Stormtroopers/Course-Capsule.git`
2. Change into the directory: `cd Course-Capsule`
3. Setup Python virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: 
    - On Linux: `source venv/bin/activate`
    - On Windows: `venv\Scripts\activate`
5. Install the required packages: `pip install -r requirements.txt`

## Running the Application

This is a client server application. The client is a simple HTML/CSS/JavaScript application that runs in the browser. The server is a Python FastAPI application that runs in the terminal. To see them in action, you will need to run both the client and the server.

### Running the Server
1. Ensure the virtual environment is activated:
    - On Linux: `source venv/bin/activate`
    - On Windows: `venv\Scripts\activate`
2. Ensure your database is up-to-date: `alembic upgrade head`
    - **Note:** This will create the database if it does not exist and apply any pending migrations. The database file `db.sqlite3` doesn't exist until you run this command for the first time. If you run into any other issues, try deleting the database file and running this command again.
3. Run the server on port 8000: `uvicorn main:app --port 8000 --reload`

### Running the Client
1. Run a simple Python HTTP server: `python -m http.server 5000`
    - Note: This must be running in a separate terminal window from the server. The server must be running at the same time.
2. Open your browser and navigate to `http://localhost:5000`
    - Note: You must see "localhost" in the URL. This is because of how the server is setup. If you see an IP address, the client will not be able to communicate with the server.

At the time of writing, there are some fake users and courses in the database. You can login with the following credentials:
- Username: `admin`
- Password: `password`

## Alembic Migrations
- Create new migration: `alembic revision --autogenerate -m "migration message"`
- Apply migrations: `alembic upgrade head`
- Downgrade migrations: `alembic downgrade -1`
- Go to specific migration: `alembic upgrade <hash>` or `alembic downgrade <hash>` where `<hash>` is the hash of the migration.
- Show migration history: `alembic history`

## Unit and Integration Test Suite

Run the test suite by running: `pytest`
    - Make sure the server is not running when you run the tests.
    - If you get an error, try reinstalling any missing requirements: `pip install -r requirements.txt`


## Directory Structure and Key Files

- `main.py`: Defines the FastAPI backend server configuration and all API endpoints.
- `pyproject.toml`: Defines linting configuration, as well as `pytest` configuration options.
- `requirements.txt`: Python package dependencies.
- `db.sqlite3`: SQLite database. This won't exist until the database is initialized.
- `alembic.ini`: Alembic configuration file.
- `alembic/`
    - `versions/`: Migrations for each database version. These allow the database to be rolled forwards or backwards to any version. Each version is a `.py` file.
- `server/`:
    - `db.py`: Setup a connection to the main database and create some sample data.
    - `models.py`: Define all database tables as SQLModel classes. Additionally, defines schemas for data that will be sent and received from the frontend web server.
    - `session_security.py`: Handle creation and decoding of session tokens.
- `index.html`: This file currently contains all HTML content, except content that is dynamically generated. It also contains a great deal of JQuery code, responsible for reactively changing content on the webpage as the user interacts with it.
- `frontend/`
    - `images/`
    - `css/`
    - `js/`
        - `CourseListPage.js`: Defines the CourseListPage class, which controls creating courses, deleting them, and retrieving them from the database.
        - `CoursePostListPage.js`: Defines the CoursePostListPage class, which controls creating posts, approving them, and retrieving a set of them from the database.
- `tests/`: Location of all unit tests.
    - `test_db.py`: Simple unit tests for database models.
    - `test_endpoints.py`: Unit and integration tests to ensure all of the API endpoints work correctly. The first part contains unit tests, while the second contains integration tests.
