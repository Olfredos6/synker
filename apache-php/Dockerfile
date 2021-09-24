FROM php:7.4-apache
RUN echo "ServerName companydir-db" >> /etc/apache2/apache2.conf && docker-php-ext-install mysqli && apachectl restart
COPY ./msql-ext.ini /usr/local/etc/php/conf.d