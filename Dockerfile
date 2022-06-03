FROM nickgryg/alpine-pandas

# Install required packages
RUN apk add --update --no-cache bash dos2unix

# Install python/pip
RUN apk add --update --no-cache python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip --upgrade
ENV PYTHONUNBUFFERED=1
# install any Python requirements used by the jobs
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

WORKDIR /usr/scheduler

# Copy files
COPY . .
COPY jobs/*.* ./jobs/
COPY crontab.* ./
COPY start.sh .

# Fix line endings && execute permissions
RUN dos2unix crontab.* *.sh jobs/*.* \
    && \
    find . -type f -iname "*.sh" -exec chmod +x {} \; \
    && \
    find . -type f -iname "*.py" -exec chmod +x {} \;

# create cron.log file
RUN touch /var/log/cron.log

# Run cron on container startup
CMD ["./start.sh"]
