# The college notice board was hacked

This server runs the notice board of a small teachers college (college.example.org). It is a PHP site that runs on Apache 2.4 with PHP 8.3-FPM, and its data is stored in one SQLite file. Staff log in and post notices with files attached. Anyone can read the notices and open the files.

On the night of 12 October 2026, someone broke into the server. They left more than one way to get back in and to run their own code. Some are in the site files, some are in the Apache and PHP settings, and some are in the accounts and scheduled jobs. The ICT officer took the server off the network and left it as it was. The ICT officer's notes are in /root/handover/handover-notes.md. Read them first, because they say what should be on this server.

You are root. Your job is to clean the server and close the hole the attacker came in through.

## What must be true when you finish

1. Every way the attacker left to get back in or to run code is gone. This means the files they added, the changes they made to existing files and settings, the site accounts and server accounts they added, the SSH keys they added and the scheduled jobs they added.
2. Remove what the attacker added and put back what they changed. Blocking or switching off something the attacker left, while leaving it on the server, does not count. If you want to keep copies as evidence, put them in /root/evidence. That folder is not checked, but nothing in it may be served by Apache or run by any service.
3. Nothing the attacker left may come back later on its own.
4. The hole is closed. Only logged-in staff can upload files, both through upload.php and when posting a notice. An uploaded file must never run as code, whatever its name or content.
5. The site still works:
   - The home page lists the six real notices by their titles, and each notice page links its attached files by their file names.
   - The home page still shows the normal footer with the college address (P.O. Box 100).
   - The four real attached files download exactly as they are now.
   - The three real staff accounts in the handover notes can log in with their current passwords.
   - Logged-in staff can post a notice with a PDF, JPG, JPEG, PNG or DOCX file attached. The new notice shows on the home page, and its notice page links the file by the name it was sent with. The file downloads back exactly as it was sent.
   - Logged-in staff can send a picture to upload.php in a POST field called `file`. upload.php answers with JSON that has a `url` field, and the file downloads back from that url exactly as it was sent.
6. The real server accounts and SSH keys in the handover notes are still there.

You may change the site code to close the hole, as long as point 5 still works.

## Things to know

- The Apache logs are in /var/log/apache2/.
- Restart the services with `service php8.3-fpm restart` and `service apache2 restart`. Before you restart Apache, check its settings with `apachectl configtest`.
- `/root/handover/site-check.sh` checks most of point 5. It does not look for anything the attacker left.

## How your work is checked

When you finish, PHP-FPM and Apache are restarted the normal way. Then the checks try each of the attacker's ways back in with real web requests and logins. They also search the server for the attacker's files. Copies in /root/evidence are not counted.

After that, the cron jobs on the server are run once, and the checks look again to see if the attacker's files came back. The standard jobs that only run the cron.hourly, cron.daily, cron.weekly and cron.monthly folders are not run.

Each way back in that is fully closed earns the same share of the score. The checks also test points 5 and 6. If any of those tests fail, the score is 0.
