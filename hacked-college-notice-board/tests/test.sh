#!/bin/bash
mkdir -p /logs/verifier
echo 0 > /logs/verifier/reward.txt

pkill -x cron 2>/dev/null || true
service apache2 stop >/dev/null 2>&1 || true
service php8.3-fpm stop >/dev/null 2>&1 || true
pkill -x apache2 2>/dev/null || true
pkill -f php-fpm 2>/dev/null || true
sleep 1

service php8.3-fpm start || echo "PHP-FPM did not start"
service apache2 start || echo "Apache did not start"
for i in $(seq 1 30); do
    python3 -c 'import urllib.request; urllib.request.urlopen("http://127.0.0.1/", timeout=3)' 2>/dev/null && break
    sleep 1
done

python3 /tests/check_site.py
