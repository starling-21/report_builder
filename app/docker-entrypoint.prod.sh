#!/bin/bash

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput


# wait for RDMS to start
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec "$@"


# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --noinput
python manage.py makemigrations reports --noinput
python manage.py migrate --noinput
python manage.py createsuperuser --noinput --username="$DJANGO_SUPERUSER_USERNAME" --email="$DJANGO_SUPERUSER_EMAIL"


# Start wsgi server
# export DEBUG=1
# python manage.py runserver 0.0.0.0:8000

export DEBUG=something_to_satisfy_gunicord_setting_or_you_get_500_error
gunicorn -b 0.0.0.0:8000 -w 3 --access-logfile - --log-level INFO 'military_site.wsgi:application'