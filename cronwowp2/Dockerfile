FROM python:2.7
RUN mkdir -p /cronwowp2/source
COPY requirements.txt /cronwowp2
WORKDIR /cronwowp2
RUN pip install -r requirements.txt
COPY source /cronwowp2/source

