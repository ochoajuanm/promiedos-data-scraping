#!/bin/bash

if [ -z "$SCHEDULER_ENVIRONMENT" ]; then
   echo "SCHEDULER_ENVIRONMENT not set, assuming Development"
   SCHEDULER_ENVIRONMENT="Development"
fi

# Select the crontab file based on the environment
CRON_FILE="crontab.$SCHEDULER_ENVIRONMENT"

echo "Loading crontab file: $CRON_FILE"

# Load the crontab file
sudo service cron start
sudo systemctl start cron
sudo systemctl status cron
grep CRON /var/log/syslog
crontab $CRON_FILE

# Start cron
echo "Starting cron..."
crond -f