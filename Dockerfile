#
# BASE STAGE:
#
FROM alpine:latest as base
ENV PYTHONUNBUFFERED=1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app/cms
ENV DJANGO_SETTINGS_MODULE cms.development
EXPOSE 5000

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
        jpeg-dev \
        py-pillow \
        py-pip \
        postgresql-libs \
        postgresql-dev \
        rust \
        g++ \
        nginx \
    && update-ca-certificates \
    && rm -rf /var/cache/apk/* \
    && pip install --upgrade pip

WORKDIR /app

COPY requirements.txt /app/
RUN pip install -r requirements.txt

#
# PROJECT FILES:
#
FROM base as projectfiles
COPY manage.py ./
COPY setupdatabase.sh ./
COPY scrapy.cfg ./
COPY cms ./app

#
# DEV:
#
FROM base as dev
COPY --from=projectfiles /app/ ./
COPY ./.git ./.git

#
# BUILD:
#
FROM dev as build
RUN python manage.py collectstatic --noinput

#
# DEPLOYMENT:
#
FROM base as deployment
RUN pip install uwsgi

RUN adduser --system -uid 102 specr
RUN chown specr:root .
#RUN chmod -R a+xr /var/log/apache2
USER specr

COPY --chown=specr:root --from=build /app/cms/sitestatic/ ./cms/sitestatic/
COPY --chown=specr:root --from=projectfiles /app/ ./
COPY nginx/specr.conf /etc/nginx/sites-available/

ENV ENABLE_REQUEST_PROFILING 1
ENV DJANGO_SETTINGS_MODULE cms.production

CMD ["sudo", "ln", "-s", "/etc/nginx/sites-available/specr.conf", "/etc/nginx/sites-enabled/"]
CMD ["/etc/init.d/nginx", "start"]
CMD ["uwsgi", "--ini", "cms/uwsgi.ini"]
