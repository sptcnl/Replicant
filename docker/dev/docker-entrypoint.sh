#!/bin/bash
set -e

# 환경변수 치환 (envsubst)
envsubst '${SERVER_NAME}' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf

# nginx 시작 (포그라운드)
exec nginx -g 'daemon off;'