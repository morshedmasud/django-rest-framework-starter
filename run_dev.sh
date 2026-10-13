#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Starting the development environment (Celery worker, beat and Django)...${NC}"

# Function to cleanup background processes on exit
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap SIGINT (Ctrl+C) and SIGTERM
trap cleanup SIGINT SIGTERM

# Start Celery Worker
echo -e "${GREEN}Starting Celery Worker...${NC}"
celery -A main worker --loglevel=info &

# Start Celery Beat
echo -e "${GREEN}Starting Celery Beat...${NC}"
celery -A main beat --loglevel=info &

# Wait a moment for Celery to start
sleep 2

# Start Django Development Server
echo -e "${GREEN}Starting Django Server...${NC}"
python manage.py runserver 0.0.0.0:8000

# If Django server stops, cleanup
cleanup
