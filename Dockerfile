# Dockerfile

FROM python:3.7-buster

# install nginx
RUN apt-get update && apt-get install nginx -y --no-install-recommends
COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

# copy source and install dependencies
RUN mkdir -p /opt/app/ && mkdir -p /opt/app/static
COPY . /opt/app/
WORKDIR /opt/app/
RUN pip install -r requirements.txt && chown -R www-data:www-data /opt/app

# start server
EXPOSE 80
STOPSIGNAL SIGTERM
CMD ["/opt/app/start-server.sh"]
