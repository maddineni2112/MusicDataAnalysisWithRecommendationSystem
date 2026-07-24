#!/usr/bin/env sh
set -eu

python manage.py collectstatic --noinput
exec gunicorn music_shell.wsgi:application --bind "0.0.0.0:${PORT:-8000}"
