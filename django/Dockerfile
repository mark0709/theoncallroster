FROM python:3.7-buster

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive
# Creating working directory
RUN mkdir /usr/local/oncall-roster
WORKDIR /usr/local/oncall-roster
# Copying requirements
COPY requirements.txt /tmp/requirements.txt
COPY django_app/ /usr/local/oncall-roster
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils \
    && apt-get install -y gcc libsasl2-dev libmariadbclient-dev curl \
    libssl-dev libldap2-dev libjpeg-dev zlib1g-dev \
    && pip install --upgrade pip \
    && pip install -r /tmp/requirements.txt \
    && find /usr/local \
        \( -type d -a -name test -o -name tests \) \
        -o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
        -exec rm -rf '{}' + \
    && rm /tmp/requirements.txt \
    && apt-get autoremove \
    && apt-get autoclean
EXPOSE 8000
CMD [ "/usr/local/bin/gunicorn", "oncall.wsgi:application", "-w", "2", "-b", ":8000" ]
