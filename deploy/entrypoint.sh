#!/bin/sh
set -e

# 添加证书自动更新检查（可选）
if [ -d "/etc/letsencrypt" ]; then
    certbot renew --quiet --post-hook "nginx -s reload"
fi

nginx
python run.py