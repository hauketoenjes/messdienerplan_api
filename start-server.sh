#!/usr/bin/env bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py crontab add

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  (python manage.py createsuperuser --no-input)
fi

# Make sure cron is enabled
service cron start

# Start the gunicorn server
(gunicorn messdienerplan_api.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
