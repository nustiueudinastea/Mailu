FROM alpine:edge

ENV LANG C.UTF-8

##
## Requirements
##

RUN echo "http://ftp.halifax.rwth-aachen.de/alpine/edge/main" > /etc/apk/repositories \
    && echo "http://ftp.halifax.rwth-aachen.de/alpine/edge/community" >> /etc/apk/repositories \
    && echo "@testing http://ftp.halifax.rwth-aachen.de/alpine/edge/testing" >> /etc/apk/repositories \
    && apk update \
    # Admin
    && apk add --no-cache --virtual build-dep openssl-dev libffi-dev python3 py3-pip python3-dev build-base \
    # Dovecot
    dovecot dovecot-sqlite dovecot-pigeonhole-plugin dovecot-pigeonhole-plugin-extdata \
    rspamd-client@testing python py-jinja2 \
    # Nginx
    nginx nginx-mod-mail python py-jinja2 certbot openssl \
    # Postfix
    postfix postfix-sqlite postfix-pcre rsyslog python py-jinja2 \
    # Redis
    redis \
    # Protos
    py-pip

 ##
 ## Mailu admin
 ##
RUN mkdir -p /mailu/admin /data /dkim
WORKDIR /mailu/admin
COPY core/admin/requirements-prod.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY core/admin/mailu ./mailu
COPY core/admin/migrations ./migrations
COPY core/admin/manage.py .
COPY core/admin/start.sh .

RUN pybabel compile -d mailu/translations

##
## Dovecot
##
RUN mkdir -p /mailu/dovecot
WORKDIR /mailu/dovecot

COPY core/dovecot/conf ./conf
COPY core/dovecot/sieve /var/lib/dovecot
COPY core/dovecot/start.py ./start.py

##
## Nginx
##
RUN mkdir -p /mailu/nginx
WORKDIR /mailu/nginx

COPY core/nginx/conf ./conf
COPY core/nginx/*.py ./

##
## Postfix
##
RUN mkdir -p /mailu/postfix
WORKDIR /mailu/postfix

COPY core/postfix/conf ./conf
COPY core/postfix/start.py ./start.py

##
## Protos
##
RUN mkdir -p /mailu/protos
WORKDIR /mailu/protos

COPY optional/protos/supervisord.conf supervisord.conf
COPY optional/protos/requirements.txt requirements.txt
RUN pip install -r requirements.txt

##
## Clean up unneeded packages
##
# RUN apk del build-dep \
#     && rm -rf /var/cache/apk/*