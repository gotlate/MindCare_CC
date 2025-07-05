#!/bin/sh
gunicorn --timeout 200 --bind 0.0.0.0:$PORT app:app