#!/bin/sh
set -e

SQLITE_DB_PATH="${SQLITE_DB_PATH:-/app/data/db.sqlite3}"
MEDIA_ROOT="${MEDIA_ROOT:-/app/media}"
STATIC_ROOT="${STATIC_ROOT:-/app/staticfiles}"

mkdir -p "$(dirname "$SQLITE_DB_PATH")" "$MEDIA_ROOT" "$STATIC_ROOT"

if [ ! -f "$SQLITE_DB_PATH" ]; then
  echo "WARNING: Production SQLite database not found at $SQLITE_DB_PATH"
  echo "WARNING: Upload your local db.sqlite3 to the persistent volume before expecting existing content."
  echo "WARNING: Migrations will run, but the site will start without imported WordPress data."
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn django_project.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
