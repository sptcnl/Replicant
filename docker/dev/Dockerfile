FROM nginx
COPY default.conf.template /etc/nginx/conf.d/default.conf
ENTRYPOINT ["/bin/bash", "-c", "envsubst 'sptcnl.duckdns.org' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]

FROM python:3.12.9

WORKDIR /app


COPY backend/ .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "config.asgi:application"]