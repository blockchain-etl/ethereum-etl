FROM python:3.6

ADD requirements.txt .
RUN pip3 install -r requirements.txt

ADD . .
ENTRYPOINT ["python3", "stream.py"]