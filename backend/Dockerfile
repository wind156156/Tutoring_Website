FROM python:3.11-slim

WORKDIR /app

# Install MySQL development headers for pymysql
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code (.env injected via docker-compose, not baked into image)
COPY . .
COPY startup.sh /app/startup.sh
RUN chmod +x /app/startup.sh

EXPOSE 8000

CMD ["/app/startup.sh"]
