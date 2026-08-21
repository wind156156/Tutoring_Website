#!/bin/sh
set -e

echo "Waiting for MySQL..."
python -c "
import time, sys
import pymysql
while True:
    try:
        conn = pymysql.connect(host='mysql', user='tutoring', password='tutoring123', database='tutoring', connect_timeout=2)
        conn.close()
        break
    except Exception:
        sys.stderr.write('.')
        sys.stderr.flush()
        time.sleep(1)
print('MySQL is ready.')
"

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
