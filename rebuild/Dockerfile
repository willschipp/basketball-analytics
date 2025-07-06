FROM python:3.12

# Set the working directory inside the container
WORKDIR /usr/local/app

# Copy only requirements first for better build caching
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY src ./src

# Optional: Expose a port (change 5000 to your app's port)
EXPOSE 5000

# Optional: Use a non-root user for security
RUN useradd app
USER app

# Default command to run your app (adjust as needed)
CMD ["python", "./src/main.py"]