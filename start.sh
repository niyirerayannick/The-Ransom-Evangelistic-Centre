#!/bin/sh
set -e

echo "Checking database path..."
echo "SQLITE_DB_PATH=${SQLITE_DB_PATH:-/app/data/db.sqlite3}"

if [ ! -f "${SQLITE_DB_PATH:-/app/data/db.sqlite3}" ]; then
  echo "WARNING: SQLite database not found at ${SQLITE_DB_PATH:-/app/data/db.sqlite3}"
  echo "The app may start with an empty database unless the persistent volume is mounted correctly."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn django_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
