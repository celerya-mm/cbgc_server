#!/bin/bash

envsubst '$APP_BASE_URL' < /tmp/default.conf > /etc/nginx/conf.d/default.conf
if [ $? -eq 0 ]; then
    nginx -g "daemon off;"
else
    echo "Error: Failed to substitute environment variables in default.conf"
    exit 1
fi
