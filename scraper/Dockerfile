FROM alpine:latest

EXPOSE 6000

RUN apk -U add \
        gcc \
        cargo \
        curl ca-certificates \
        libffi-dev \
        libxml2-dev \
        libxslt-dev \
        musl-dev \
        libressl-dev \
        python3-dev \
        py-pillow \
        py-pip \
        postgresql-libs \
        postgresql-dev \
        rust \
    && update-ca-certificates \
    && rm -rf /var/cache/apk/* \
    && pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/
