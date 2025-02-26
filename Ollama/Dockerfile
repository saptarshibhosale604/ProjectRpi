# Use the official Python image from the Docker Hub
#FROM python:3.9-slim
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application code into the container
COPY app.py .

# Command to run your application
CMD ["python", "app.py"]
