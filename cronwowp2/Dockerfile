FROM python:2.7
RUN apt-get update && apt-get install -y cron
RUN mkdir -p /cronwowp2/source
COPY requirements.txt /cronwowp2
COPY crontab /etc/cron.d/cronwow
RUN chmod 644 /etc/cron.d/cronwow
RUN touch /var/log/cronwowp2.log
WORKDIR /cronwowp2
RUN pip install -r requirements.txt
COPY source /cronwowp2/source
ENTRYPOINT ["cron", "-f"]
CMD ["python", "source/models.py"]
