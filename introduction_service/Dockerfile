# Use an official Python runtime as a parent image
FROM python:3.9

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy .env file into the image
#COPY .env /app/.env

# Set environment variables directly in Docker
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Install any dependencies specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 5001 available to the world outside this container
EXPOSE 5001

# Run app.py when the container launches
CMD ["python", "app.py"]
