FROM alpine:edge

RUN apk add --no-cache python py-jinja2 rspamd rspamd-controller rspamd-proxy ca-certificates

RUN mkdir /run/rspamd

COPY conf/ /conf
COPY local_conf/ /local_conf
COPY start.py /start.py

CMD /start.py
