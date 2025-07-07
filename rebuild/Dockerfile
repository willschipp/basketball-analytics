FROM python:3.12-slim

# update for dependencies
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0

# Set the working directory inside the container
WORKDIR /usr/local/app

# Copy only requirements first for better build caching
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY src ./src


# Use a non-root user for security
RUN useradd --create-home app

# own the directory
RUN chown -R app:app /usr/local/app /tmp

# Expose a port (change 5000 to your app's port)
EXPOSE 5000

# switch user
USER app

# Default command to run your app (adjust as needed)
CMD ["python", "./src/main.py"]