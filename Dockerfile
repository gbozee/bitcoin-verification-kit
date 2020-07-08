from python:3.8

ADD requirements.txt /
RUN pip install -U pip 
RUN pip install -r /requirements.txt
RUN pip install gunicorn

ADD . /web-app
WORKDIR /web-app

CMD gunicorn --workers=1 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 index:app --access-logfile -
