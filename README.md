# Introduction
This is the backend of a benchmarking tool for hackathon organizers, where they can upload and analyze participant surveys.

# Prerequisites
- Edit the allowed origins in src/main.py, line 12 with the origins that you want to access the application from
- If you want to access interactive docs, remove the configuration from the constructor call in line 8 of src/main.py

# How to get it running
1. Install and run MongoDB
2. Clone this repo
3. Create a .env file in the root directory
4. Create a SECRET_KEY variable in the .env file with a secret key
5. Create a DB_CONNECTION variable in the .env file with the connection string of your MongoDB instance
6. Install dependencies with `pip install --no-cache-dir --upgrade -r /code/requirements.txt`
7. Run development server with `uvicorn src.main:app --reload`

# How to run it in a Docker container
1. Install and run MongoDB
2. Install Docker
3. Build a Docker image from this repo with `docker build https://github.com/robertsauter/hack-eval-api.git -t hackevalapi`
4. Run the image with `docker run -p 8000:8000 --name hackevalapi -e SECRET_KEY=<your_secret_key> -e DB_CONNECTION=<your_db_connection_string>`. Paste in a secret key and the connection string of your MongoDB instance

# How to run it with Docker Compose
1. Install Docker
2. Clone this repo
3. Create a .env file in the root directory
4. Create a SECRET_KEY variable in the .env file with a secret key
5. Create a DB_CONNECTION variable in the .env file with the connection string to MongoDB (mongodb://mongo:27017)
6. Run with `docker compose up`