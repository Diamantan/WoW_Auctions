FROM python:2.7
RUN apt-get update && apt-get install -y cron
RUN mkdir -p /cronwowp2/source
COPY requirements.txt /cronwowp2
COPY crontab /etc/cron.d/cronwow
RUN chmod 644 /etc/cron.d/cronwow
RUN touch /var/log/cron.log
WORKDIR /cronwowp2
RUN pip install -r requirements.txt
COPY source /cronwowp2/source
WORKDIR /cronwowp2/source
CMD python models.py && cron && tail -f /dev/null 
