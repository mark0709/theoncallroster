FROM python:3.7-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive
# Creating working directory
WORKDIR /usr/local/oncall-roster
CMD [ "/usr/local/bin/celery", "worker", "-A", "oncall", "-l", "info", "--uid", "65534" ]
