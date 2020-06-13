#!/bin/bash

# Collect static files
echo "Collecting static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate --noinput
python manage.py makemigrations reports --noinput
python manage.py migrate --noinput



# Start server
#echo "Starting server"
python manage.py runserver 0.0.0.0:8000
