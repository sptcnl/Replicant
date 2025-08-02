FROM nginx

COPY nginx/conf.d/default.conf.template /etc/nginx/conf.d/default.conf.template
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["./docker-entrypoint.sh"]

FROM python:3.12.9

WORKDIR /app


COPY backend/ .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]