# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirement.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir: Disables the cache, which reduces the image size.
# --upgrade pip: Ensures we have the latest version of pip.
RUN pip install --no-cache-dir --upgrade pip -r requirement.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Define the command to run the application
# Uvicorn is an ASGI server, ideal for FastAPI.
# --host 0.0.0.0: Makes the server accessible from outside the container.
# --port 8000: The port to run on.
# main:app: Tells uvicorn to look for an object named 'app' in a file named 'main.py'.
# You should change 'main:app' to match your main application file and instance.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
