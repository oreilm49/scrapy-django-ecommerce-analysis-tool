#
# BASE STAGE:
#
FROM python:3.9-buster as base
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH /app/cms
ENV DJANGO_SETTINGS_MODULE cms.settings
EXPOSE 8000

RUN apt-get update && apt-get install --no-install-recommends -y \
        vim gettext libxml2-dev libxslt1-dev zlib1g-dev libffi-dev \
        libssl-dev libzbar-dev apache2 apache2-dev poppler-utils \
        && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

#
# PROJECT FILES:
#
FROM base as projectfiles
COPY manage.py ./
COPY setupdatabase.sh ./
COPY scrapy.cfg ./
COPY ./cms ./cms

#
# DEV:
#
FROM base as dev
COPY requirements-dev.txt /app/
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY --from=projectfiles /app/ ./
COPY ./.git ./.git

#
# BUILD:
#
FROM dev as build
RUN python3 manage.py collectstatic --noinput

#
# DEPLOYMENT:
#
FROM base as deployment
RUN pip install --no-cache-dir mod-wsgi==4.7.1

RUN adduser --system -uid 102 specr
RUN chown specr:root .
RUN chmod -R a+xr /var/log/apache2
USER specr

COPY --chown=specr:root --from=build /app/cms/sitestatic/ ./cms/sitestatic/
COPY --chown=specr:root --from=projectfiles /app/ ./
COPY --chown=specr:root specr.conf ./specr.conf

ENV DJANGO_SETTINGS_MODULE cms.production

CMD ["mod_wsgi-express", "start-server", "cms/wsgi.py", "--url-alias", "/static", "cms/sitestatic/", "--url-alias", "/media", "cms/media/", "--trust-proxy-header", "X-Forwarded-Proto", "--port", "8000", "--threads", "10", "--processes", "1", "--socket-timeout", "600", "--request-timeout", "600", "--limit-request-body", "104857600", "--log-to-terminal", "--log-level", "info", "--access-log", "--enable-sendfile", "--include-file", "specr.conf", "--locale", "C.UTF-8"]
