# Handover notes for the notice board server

Written by Grace Nanjala (ICT Officer) on 14 October 2026.

## What happened

On the morning of 14 October 2026 a lecturer told me that the notice board was slow and that it "looked strange". When I looked at the Apache access log I saw requests to a PHP file in the uploads folder. None of us uploaded that file. I did not delete or change anything. I took the server off the public network and left it as it was, so that you can look at it.

## The server

- Ubuntu 24.04 with Apache 2.4 and PHP 8.3-FPM. Apache sends .php files to PHP-FPM over the socket /run/php/php8.3-fpm.sock.
- The site is in /var/www/college.example.org. The web root is the public folder. The database is one SQLite file, database/college.sqlite.
- There is one Apache virtual host, college.example.org. Apart from that, Apache uses the Ubuntu default config, plus servername.conf that I added to stop the ServerName warning.
- The only thing we set in public/.user.ini is a bigger upload size (upload_max_filesize and post_max_size).
- PHP-FPM uses the Ubuntu default settings. We did not change them.
- We never added any cron jobs. Only the jobs that come with the Ubuntu packages should be there.
- To restart the services: `service php8.3-fpm restart` and `service apache2 restart`.

## How the site works

- Anyone can read the notices on the home page and open the attached files.
- Staff log in at /login.php. From the dashboard they can post a notice and attach a file.
- The notice editor sends pictures to /upload.php. It sends the file in a POST field called `file`, and upload.php answers with JSON that has a `url` field where the file can be downloaded.
- Staff attach PDF, JPG, JPEG, PNG and DOCX files. Nothing else is needed.

## Real staff accounts on the site

| Username | Name | Role |
|---|---|---|
| ict.officer | Grace Nanjala | admin |
| registrar | Mary Achieng | staff |
| dean.students | Peter Ekal | staff |

Please do not change any staff password. To check the site you can log in as registrar with the password `Registrar#2026`.

## Real server accounts and SSH keys

- root: only my key, `grace@ict-laptop`, SHA256:/w7ytMQTl3Q/pmlkRhLyewIIpwTPoKmZTnfgqnd+gmc
- ubuntu: this is our deploy account. Only the deploy key, `deploy@college-ci`, SHA256:hTl+mt2Zn7X0o7qA0LfFXWq0qrqFDBcXUuCVcv2cT5I
- All the other accounts in /etc/passwd should be the normal system accounts that come with Ubuntu and its packages (www-data, backup, nobody and so on). None of them is used to log in.

## Checking the site

`/root/handover/site-check.sh` checks that the home page, the notices, the attached files, the registrar login and upload.php still work. It does not look for anything the attacker left.
