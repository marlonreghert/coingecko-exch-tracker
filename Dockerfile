FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src:$PYTHONPATH"

# Install necessary tools
RUN apt-get update && apt-get install -y cron python3 python3-pip && apt-get clean

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/

# Install Python dependencies
RUN   /usr/local/bin/python3  -m pip install --no-cache-dir -r requirements.txt &&  /usr/local/bin/python3  -m pip list

# Add cron job
RUN echo "*/1 * * * * PYTHONPATH=/app  /usr/local/bin/python3  -m src.table_updater >> /var/log/cron.log 2>&1" > /etc/cron.d/table_updater_cron

# Set permissions and apply cron job
RUN chmod 0644 /etc/cron.d/table_updater_cron && crontab /etc/cron.d/table_updater_cron

# Create log file
RUN touch /var/log/cron.log

# Start cron and log output
CMD ["sh", "-c", "cron && tail -f /var/log/cron.log"]
