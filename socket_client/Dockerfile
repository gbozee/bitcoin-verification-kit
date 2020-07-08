from python:3.8-alpine

ADD requirements.txt /
RUN pip install -U pip 
RUN pip install -r /requirements.txt

ADD web_sockets.py /

CMD python /web_sockets.py
