#!/bin/bash

if [ -z "$SCHEDULER_ENVIRONMENT" ]; then
   echo "SCHEDULER_ENVIRONMENT not set, assuming Development"
   SCHEDULER_ENVIRONMENT="Development"
fi

# Select the crontab file based on the environment
CRON_FILE="crontab.$SCHEDULER_ENVIRONMENT"

echo "Loading crontab file: $CRON_FILE"

# Load the crontab file
service cron start
systemctl start cron
systemctl status cron
grep CRON /var/log/syslog
ls
crontab $CRON_FILE >> file.txt

# Start cron
echo "Starting cron..."
crond -f >> file1.txt

cat file.txt
cat file1.txt