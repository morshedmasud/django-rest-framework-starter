#!/bin/bash
# Run migrations, then load every fixture in seed/ (if the folder exists).
set -e
python3 manage.py migrate
if [ -d seed ]; then
    for fixture in seed/*; do
        [ -f "$fixture" ] || continue
        echo "Seeding $fixture"
        python3 manage.py loaddata "$fixture"
    done
fi
