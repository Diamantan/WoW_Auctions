FROM python:2.7
RUN mkdir -p /webwowp2/source
COPY requirements.txt /webwowp2
WORKDIR /webwowp2
RUN pip install -r requirements.txt
COPY source /webwowp2/source
WORKDIR /webwowp2/source
CMD ["python", "web.py"]

