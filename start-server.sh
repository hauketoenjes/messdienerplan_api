#!/usr/bin/env bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input

if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  (python manage.py createsuperuser --no-input)
fi

# Check if KaPlan shall be polled, if so install cronjob, otherwise remove cronjob (if container is being restarted)
if [ -z "$POLL_KAPLAN" ]; then
  crontab -l | {
    cat
    echo "*/15 * * * * /opt/app/manage.py poll_kaplan"
  } | crontab -

else
  crontab -r
fi

# Start the gunicorn server
(gunicorn messdienerplan_api.wsgi --user www-data --bind 0.0.0.0:8010 --workers 3) &
nginx -g "daemon off;"
