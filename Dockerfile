# pull official base image
FROM python:3.6.6-alpine3.6

# set work directory
WORKDIR .

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN apk add --update --no-cache g++ gcc libxslt-dev libxml2-dev libxslt-dev py-cryptography musl-dev libffi-dev openssl-dev python3-dev
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .
RUN rm -rf neo4j