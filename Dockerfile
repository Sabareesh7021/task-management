# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    gcc \
    && apt-get clean

# Set the working directory
WORKDIR /app

# Copy the project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install gunicorn

# Expose port
EXPOSE 8001

# Use Gunicorn to serve the app
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8001", "--reload"]
