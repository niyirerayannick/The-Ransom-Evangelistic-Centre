#!/bin/sh
set -e

DB_PATH="${SQLITE_DB_PATH:-/app/data/db.sqlite3}"

echo "Checking database path..."
echo "SQLITE_DB_PATH=${DB_PATH}"

if [ ! -f "${DB_PATH}" ]; then
  echo "ERROR: SQLite database not found at ${DB_PATH}"
  echo "Upload your local db.sqlite3 to the server persistent volume before starting."
  echo "See DEPLOYMENT_COOLIFY.md section B (Copy local database and media)."
  exit 1
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn django_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
