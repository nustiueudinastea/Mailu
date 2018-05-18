#!/bin/sh

python3 manage.py advertise
python3 manage.py db upgrade
exec gunicorn -w 4 -b 127.0.0.1:8080 --access-logfile - --error-logfile - --preload mailu:app
