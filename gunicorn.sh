#!/bin/sh

echo Starting app...
gunicorn -w 4 --threads 4 --log-config gunicorn/gunicorn_logging.conf -b 0.0.0.0:5000 --reload wsgi:app
