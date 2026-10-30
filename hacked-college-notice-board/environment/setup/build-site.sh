#!/bin/bash
set -euo pipefail

SITE=/var/www/college.example.org

ln -sf /usr/share/zoneinfo/Africa/Nairobi /etc/localtime
echo Africa/Nairobi > /etc/timezone

mkdir -p "$SITE/database"
php /tmp/setup/seed.php "$SITE/database/college.sqlite"
chown -R root:root "$SITE"
find "$SITE" -type d -exec chmod 755 {} +
find "$SITE" -type f -exec chmod 644 {} +
chown -R www-data:www-data "$SITE/database" "$SITE/public/uploads"
chmod 775 "$SITE/database"
chmod 664 "$SITE/database/college.sqlite"

a2enmod -q proxy_fcgi setenvif rewrite headers
a2dissite -q 000-default
a2ensite -q college.example.org
echo "ServerName localhost" > /etc/apache2/conf-available/servername.conf
a2enconf -q servername

install -d -m 700 -o ubuntu -g ubuntu /home/ubuntu/.ssh
install -m 600 -o ubuntu -g ubuntu /tmp/setup/keys/deploy.pub /home/ubuntu/.ssh/authorized_keys
install -d -m 700 /root/.ssh
install -m 600 /tmp/setup/keys/grace.pub /root/.ssh/authorized_keys

chown -R root:root /root/handover
chmod 700 /root/handover
chmod 600 /root/handover/handover-notes.md
chmod 700 /root/handover/site-check.sh
chmod 755 /usr/local/sbin/start-site

/usr/local/sbin/start-site true
for i in $(seq 1 20); do
    curl -fsS -o /dev/null http://127.0.0.1/ && break
    sleep 1
done
curl -fsS http://127.0.0.1/ | grep -q 'Sports Day Photos'
service apache2 stop >/dev/null 2>&1 || true
service php8.3-fpm stop >/dev/null 2>&1 || true
rm -f /var/log/apache2/*.log /var/log/php8.3-fpm.log /var/lib/php/sessions/sess_*
