# Course Capsule

## Setup Instructions
1. Clone the repository: `git clone git@github.com:CSCI375-Stormtroopers/Course-Capsule.git`
2. Change into the directory: `cd Course-Capsule`
3. Setup Python virtual environment: `python3 -m venv venv`
4. Activate the virtual environment: `source venv/bin/activate`
5. Install the required packages: `pip install -r requirements.txt`

## Running the Application

This is a client server application. The client is a simple HTML/CSS/JavaScript application that runs in the browser. The server is a Python FastAPI application that runs in the terminal. To see them in action, you will need to run both the client and the server.

### Running the Server
1. Ensure the virtual environment is activated: `source venv/bin/activate`
2. Ensure your database is up-to-date: `alembic upgrade head`
3. Run the server on port 8000: `uvicorn server:app --port 8000 --reload`

### Running the Client
1. Run a simple Python HTTP server: `python -m http.server 5000`
2. Open your browser and navigate to `http://localhost:5000`
    - Note: You must see "localhost" in the URL. This is because of how the server is setup. If you see an IP address, the client will not be able to communicate with the server.

At the time of writing, there are some fake users and courses in the database. You can login with the following credentials:
- Username: `admin`
- Password: `password`
