FROM alpine:edge

ENV LANG C.UTF-8
ENV SHELL /bin/sh

##
## Requirements
##

# Build deps
RUN echo "http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk --update add --no-cache --virtual build-dep openssl-dev libffi-dev build-base linux-headers \
    # Protos
    python python-dev py-pip git \
    # Admin
    python3 python3-dev py3-pip \
    # Dovecot
    dovecot dovecot-sqlite dovecot-pigeonhole-plugin dovecot-pigeonhole-plugin-extdata \
    rspamd-client python py-jinja2 \
    # Nginx
    nginx nginx-mod-mail openssl \
    # Postfix
    postfix postfix-sqlite postfix-pcre rsyslog python py-jinja2 \
    # Redis
    redis \
    # Rainloop
    unzip php5-fpm php5-dom php5-curl php5-iconv php5-json

# PHP config
ENV PHP_MEMORY_LIMIT    512M
ENV MAX_UPLOAD          50M
ENV PHP_MAX_FILE_UPLOAD 200
ENV PHP_MAX_POST        100M

RUN	sed -i "s|;*daemonize\s*=\s*yes|daemonize = no|g" /etc/php5/php-fpm.conf && \
	sed -i "s|;*listen\s*=\s*127.0.0.1:9000|listen = 9000|g" /etc/php5/php-fpm.conf && \
	sed -i "s|;*listen\s*=\s*/||g" /etc/php5/php-fpm.conf && \
	sed -i "s|;*memory_limit =.*|memory_limit = ${PHP_MEMORY_LIMIT}|i" /etc/php5/php.ini && \
    sed -i "s|;*upload_max_filesize =.*|upload_max_filesize = ${MAX_UPLOAD}|i" /etc/php5/php.ini && \
    sed -i "s|;*max_file_uploads =.*|max_file_uploads = ${PHP_MAX_FILE_UPLOAD}|i" /etc/php5/php.ini && \
    sed -i "s|;*post_max_size =.*|post_max_size = ${PHP_MAX_POST}|i" /etc/php5/php.ini && \
    sed -i "s|;*cgi.fix_pathinfo=.*|cgi.fix_pathinfo= 0|i" /etc/php5/php.ini && \
	mkdir -p /www

RUN pip install pipenv==11.6.1

##
## Mailu admin
##
RUN mkdir -p /mailu/admin /data /dkim
WORKDIR /mailu/admin
COPY core/admin/requirements-prod.txt requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install git+git://github.com/nustiueudinastea/protoslib-py.git#egg=protoslib

COPY core/admin/mailu ./mailu
COPY core/admin/migrations ./migrations
COPY core/admin/manage.py .
COPY core/admin/start.sh .

RUN pybabel compile -d mailu/translations

##
## Dovecot
##
RUN mkdir -p /mailu/dovecot /mail /overrides
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
## Rainloop
##

ENV RAINLOOP_URL https://github.com/RainLoop/rainloop-webmail/releases/download/v1.11.3/rainloop-community-1.11.3.zip

RUN rm -rf /var/www/html/ \
 && mkdir -p /var/www/html \
 && mkdir -p /mailu/rainloop \
 && cd /var/www/html \
 && wget ${RAINLOOP_URL} \
 && unzip *.zip \
 && rm -f *.zip \
 && find . -type d -exec chmod 755 {} \; \
 && find . -type f -exec chmod 644 {} \;

COPY webmails/rainloop/include.php /var/www/html/include.php
COPY webmails/rainloop/php.ini /usr/local/etc/php/conf.d/rainloop.ini

COPY webmails/rainloop/config.ini /mailu/rainloop/config.ini
COPY webmails/rainloop/default.ini /mailu/rainloop/default.ini

COPY webmails/rainloop/start.sh /mailu/rainloop/start.sh

##
## Protos
##
RUN mkdir -p /mailu/protos /certs
WORKDIR /mailu/protos

COPY optional/protos/* ./
RUN pipenv install --three

##
## Clean up unneeded packages
##
# RUN apk del build-dep \
#     && rm -rf /var/cache/apk/*