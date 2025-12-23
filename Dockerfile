# Use Python 3.11 slim (more stable with psycopg2-binary + Postgres)
FROM python:3.11-slim

# Avoid .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir inside the container
WORKDIR /app

# System dependencies:
# - build-essential / gcc: compile any wheels if needed
# - libpq-dev: Postgres client libs for psycopg2-binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Default arguments for your pipeline script
# main.py usage: python main.py <hours_back> <top_n_articles>
ENV HOURS_BACK=24 \
    TOP_N=10

# Command: ensure DB tables and run the daily pipeline
CMD ["bash", "-c", "python main.py ${HOURS_BACK} ${TOP_N}"]
