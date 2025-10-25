#!/bin/bash

# This script starts the Gunicorn server in the background for deployment.

echo "Stopping any existing Gunicorn processes..."
# The '|| true' prevents the script from exiting if no processes are found
pkill gunicorn || true
sleep 2

echo "Starting Gunicorn as a background daemon..."

# --workers 3: Number of worker processes. A good starting point is (2 x number_of_cores) + 1.
# --daemon: Runs the process in the background.
# --log-file gunicorn.log: Specifies the file to log output to.
# --log-level info: Sets the logging level.
gunicorn my_backend.wsgi:application \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --daemon \
    --log-file gunicorn.log \
    --log-level info

echo "Gunicorn has been started."
echo "You can check the logs with: tail -f gunicorn.log"
echo "To see the running processes, use: ps aux | grep gunicorn"
