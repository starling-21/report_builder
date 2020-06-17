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





# Start server
#echo "Starting server"
python manage.py runserver 0.0.0.0:8000




#----------------------  run MIGRATIONS if there are input args after .manage.py
#if [[ $# -gt 0 ]]; then
#    RUN ./manage.py "$@"
#else
#    RUN ./manage.py makemigrations
#    RUN ./manage.py migrate
#    RUN ./manage.py createcustomsuperuser  # self-made
#
#    RUN ./manage.py runserver 0.0.0.0:8000
#fi
