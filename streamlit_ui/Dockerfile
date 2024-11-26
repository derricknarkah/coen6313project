# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Streamlit app code
COPY . .

# Expose Streamlit's default port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false"]
