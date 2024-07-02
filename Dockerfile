# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables  
# Disable output buffering and prevent the creation of .pyc files
ENV PYTHONUNBUFFERED=1     
ENV PYTHONDONTWRITEBYTECODE=1 

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt /app/

# Install the dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the entire project into the container
COPY . /app/

# Copy the .env file into the container
COPY .env /app/.env

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]