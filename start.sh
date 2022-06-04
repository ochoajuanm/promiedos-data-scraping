#!/bin/bash

if [ -z "$SCHEDULER_ENVIRONMENT" ]; then
   echo "SCHEDULER_ENVIRONMENT not set, assuming Development"
   SCHEDULER_ENVIRONMENT="Development"
fi

# Select the crontab file based on the environment
CRON_FILE="crontab.$SCHEDULER_ENVIRONMENT"

echo "Loading crontab file: $CRON_FILE"

# Load the crontab file
crontab $CRON_FILE
ls
echo "----"
ls ~
echo "----"
ls /usr/scheduler/jobs/
echo "----"
ls /var/spool/cron
echo "----"
ls /var/spool/cron/crontabs
echo "----"
ls /etc/cron.d
echo "----"
ls /etc/anacrontab
echo "----"

python3 /usr/scheduler/jobs/main.py

# Start cron
echo "Starting cron..."
crond -f