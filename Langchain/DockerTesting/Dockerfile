# Use the official Python image from the Docker Hub
#FROM python:3.9-slim
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install -r requirements.txt

# Cop.st of your application code into the container
COPY . .

# Command to run your application
CMD ["python", "35_toolFinanceAssist.py"]
