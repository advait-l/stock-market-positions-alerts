# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at the root of the app directory
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size.
# --trusted-host pypi.python.org: Can help in some network environments.
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt

# Copy the rest of your application's code from the local 'app' directory
# to the 'app' directory in the container
COPY ./app ./app

# Make port 8000 available to the world outside this container.
# Cloud Run will automatically receive requests on this port.
EXPOSE 8000

# Run the application using gunicorn.
# This is a production-ready WSGI server.
# We bind to 0.0.0.0 to accept connections from any IP address.
# The 'app.main:app' part should correspond to your file and FastAPI app instance.
# Example: If your main file is `main.py` and the app is `app = FastAPI()`, this would be `main:app`.
# I will assume the entry point is `app.main:app` based on the project structure.
CMD ["gunicorn", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "app.main:app"] 