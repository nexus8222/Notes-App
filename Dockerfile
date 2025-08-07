# Dockerfile

# --- Build Stage ---
# Use a full Python image to build our dependencies
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install system dependencies that might be needed by Python packages
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# --- Final Stage ---
# Use a smaller, non-root base image for the final application
FROM python:3.11-slim

# Create a non-root user for security
RUN addgroup --system app && adduser --system --group app

# Set environment variables
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# Install dependencies from the build stage
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application source code
COPY . .

# Change ownership of the files to the non-root user
RUN chown -R app:app $APP_HOME

# Switch to the non-root user
USER app

# Expose the port the app runs on
EXPOSE 8000

# Run the application with Gunicorn (a production-ready web server)
# The --bind 0.0.0.0 is crucial for Docker networking.
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "noteapp.wsgi:application"]

