FROM python:3.10-slim-buster

WORKDIR /usr/src/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir --upgrade -r requirements.txt

RUN groupadd -r flask-user && \
    useradd -g flask-user flask-user

RUN chown -R flask-user:flask-user /usr/src/app && \
    chmod -R 744 /usr/src/app

USER flask-user