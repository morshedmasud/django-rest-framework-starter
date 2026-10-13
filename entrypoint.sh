#!/bin/sh
# Prepares the app, then runs the container command (uvicorn by default).
# Set RUN_MIGRATIONS=0 on worker containers so only the web container migrates.
set -e

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    # Wait for the database to accept connections (up to ~60s).
    tries=0
    until python manage.py migrate --noinput; do
        tries=$((tries + 1))
        if [ "$tries" -ge 30 ]; then
            echo "Database not reachable, giving up." >&2
            exit 1
        fi
        echo "Waiting for database... ($tries)"
        sleep 2
    done

    python manage.py collectstatic --noinput

    if [ -n "$ADMIN_EMAIL" ] && [ -n "$ADMIN_PASSWORD" ]; then
        python manage.py create_super_user
    fi
fi

exec "$@"
