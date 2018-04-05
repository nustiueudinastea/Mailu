#!/bin/sh

DATA_DIR=/data/rainloop

# There is no cleaner way to setup the default SMTP/IMAP server or to
# override the configuration
rm -f ${DATA_DIR}/_data_/_default_/domains/*
mkdir -p ${DATA_DIR}/_data_/_default_/domains/ ${DATA_DIR}/_data_/_default_/configs/
cp /mailu/rainloop/default.ini ${DATA_DIR}/_data_/_default_/domains/
cp /mailu/rainloop/config.ini ${DATA_DIR}/_data_/_default_/configs/

# Fix some permissions
chown -R nobody:nobody ${DATA_DIR}

# Run apache
exec /usr/bin/php-fpm5
