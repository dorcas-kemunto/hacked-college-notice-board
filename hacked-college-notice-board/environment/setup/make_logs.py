import random
from datetime import datetime, timedelta, timezone

rnd = random.Random(20261012)
EAT = timezone(timedelta(hours=3))
START = datetime(2026, 10, 5, 0, 0, tzinfo=EAT)
END = datetime(2026, 10, 14, 9, 30, tzinfo=EAT)

BROWSERS = [
    "Mozilla/5.0 (Linux; Android 14; SM-A146B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; TECNO KI5q) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Mobile/15E148 Safari/604.1",
]
GOOGLEBOT = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
SCANNER = "Mozilla/5.0 zgrab/0.x"
SITE = "http://college.example.org"

NOTICE_SIZES = {1: 1712, 2: 1748, 3: 1630, 4: 1705, 5: 1594, 6: 1661}
ATTACHMENTS = {
    1: ("/uploads/2026/09/term-dates-2026.pdf", 933),
    2: ("/uploads/2026/09/fees-structure-2026-2027.pdf", 932),
    4: ("/uploads/2026/09/tp-allocation-2026.docx", 1058),
    5: ("/uploads/2026/10/sports-day-2026.jpg", 11690),
}
VISITORS = [f"198.51.100.{n}" for n in rnd.sample(range(2, 250), 45)] + \
           [f"192.0.2.{n}" for n in rnd.sample(range(20, 250), 20)]
STAFF_IP = "192.0.2.10"
SCANNER_IPS = [f"198.51.100.{n}" for n in (251, 252, 253)]
ATTACKER = "203.0.113.77"
ATTACKER2 = "203.0.113.140"

events = []


def add(when, ip, method, path, status, size, ua, referer="-"):
    events.append((when, ip, method, path, status, size, ua, referer))


def visit(when, ip, ua):
    add(when, ip, "GET", "/", 200, 1984 + rnd.randint(-6, 6), ua)
    t = when + timedelta(seconds=rnd.randint(1, 3))
    add(t, ip, "GET", "/assets/style.css", rnd.choice([200, 304]), 812, ua, SITE + "/")
    for _ in range(rnd.choice([0, 1, 1, 1, 2])):
        t += timedelta(seconds=rnd.randint(5, 90))
        nid = rnd.choice([1, 2, 3, 4, 5, 6, 6, 6, 4, 2])
        add(t, ip, "GET", f"/notice.php?id={nid}", 200, NOTICE_SIZES[nid], ua, SITE + "/")
        if nid in ATTACHMENTS and rnd.random() < 0.6:
            t += timedelta(seconds=rnd.randint(3, 40))
            path, size = ATTACHMENTS[nid]
            add(t, ip, "GET", path, 200, size, ua, f"{SITE}/notice.php?id={nid}")


def staff_login(when, ua):
    add(when, STAFF_IP, "GET", "/login.php", 200, 1530, ua, SITE + "/")
    add(when + timedelta(seconds=14), STAFF_IP, "POST", "/login.php", 302, 0, ua, SITE + "/login.php")
    add(when + timedelta(seconds=15), STAFF_IP, "GET", "/dashboard.php", 200, 1490, ua, SITE + "/login.php")


t = START
while t < END:
    hour = t.hour
    rate = 9 if 7 <= hour <= 21 else 1
    for _ in range(rnd.randint(0, rate)):
        visit(t + timedelta(seconds=rnd.randint(0, 3599)), rnd.choice(VISITORS), rnd.choice(BROWSERS))
    t += timedelta(hours=1)

for day in range(9):
    base = START + timedelta(days=day, hours=rnd.randint(0, 23), minutes=rnd.randint(0, 59))
    add(base, "66.249.66.%d" % rnd.randint(1, 200), "GET", "/robots.txt", 200, 63, GOOGLEBOT)
    add(base + timedelta(seconds=4), "66.249.66.%d" % rnd.randint(1, 200), "GET", "/", 200, 1984, GOOGLEBOT)

for _ in range(40):
    when = START + timedelta(seconds=rnd.randint(0, int((END - START).total_seconds())))
    path = rnd.choice(["/wp-login.php", "/.env", "/.git/config", "/phpmyadmin/", "/admin.php",
                       "/xmlrpc.php", "/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php"])
    add(when, rnd.choice(SCANNER_IPS), "GET", path, 404, 274, SCANNER)

for day, hh, mm in [(0, 8, 41), (1, 9, 5), (2, 8, 57), (3, 14, 20), (4, 10, 2), (7, 8, 49), (8, 9, 12)]:
    staff_login(START + timedelta(days=day, hours=hh, minutes=mm), BROWSERS[2])
posted = datetime(2026, 10, 9, 10, 11, 20, tzinfo=EAT)
add(posted, STAFF_IP, "GET", "/post-notice.php", 200, 1688, BROWSERS[2], SITE + "/dashboard.php")
add(posted + timedelta(seconds=40), STAFF_IP, "POST", "/post-notice.php", 302, 0, BROWSERS[2], SITE + "/post-notice.php")
add(posted + timedelta(seconds=41), STAFF_IP, "GET", "/notice.php?id=6", 200, 1661, BROWSERS[2], SITE + "/post-notice.php")

FF = "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0"
PY = "python-requests/2.31.0"
CURL = "curl/8.5.0"
SHELL = "/uploads/2026/10/scan_0412.php"


def at(hh, mm, ss, day=12):
    return datetime(2026, 10, day, hh, mm, ss, tzinfo=EAT)


attack = [
    (at(1, 9, 12), ATTACKER, "GET", "/robots.txt", 200, 63, FF),
    (at(1, 9, 15), ATTACKER, "GET", "/", 200, 1984, FF),
    (at(1, 9, 31), ATTACKER, "GET", "/notice.php?id=5", 200, 1594, FF),
    (at(1, 9, 58), ATTACKER, "GET", "/login.php", 200, 1530, FF),
    (at(1, 10, 2), ATTACKER, "GET", "/upload.php", 400, 31, PY),
    (at(1, 11, 39), ATTACKER, "POST", "/upload.php", 200, 47, PY),
    (at(1, 11, 44), ATTACKER, "GET", SHELL + "?c=id", 200, 70, PY),
    (at(1, 12, 3), ATTACKER, "GET", SHELL + "?c=uname%20-a", 200, 118, PY),
    (at(1, 12, 30), ATTACKER, "GET", SHELL + "?c=cat%20../../../../includes/config.php", 200, 248, PY),
    (at(1, 13, 10), ATTACKER, "GET", SHELL + "?c=ls%20-la%20/var/www/college.example.org/database", 200, 297, PY),
    (at(1, 20, 55), ATTACKER, "POST", SHELL, 200, 12, PY),
    (at(1, 24, 18), ATTACKER, "POST", SHELL, 200, 1840, PY),
    (at(1, 29, 40), ATTACKER, "POST", SHELL, 200, 11, PY),
    (at(1, 33, 47), ATTACKER, "GET", "/uploads/staff-photo.jpg", 200, 1219, PY),
    (at(1, 34, 10), ATTACKER, "POST", "/uploads/staff-photo.jpg", 200, 1236, PY),
    (at(1, 40, 12), ATTACKER, "GET", "/login.php", 200, 1530, FF),
    (at(1, 41, 30), ATTACKER, "POST", "/login.php", 302, 0, FF),
    (at(1, 41, 31), ATTACKER, "GET", "/dashboard.php", 200, 1494, FF),
    (at(1, 42, 2), ATTACKER, "GET", "/logout.php", 302, 0, FF),
    (at(1, 49, 6), ATTACKER, "POST", SHELL, 200, 9, PY),
    (at(2, 2, 19), ATTACKER2, "POST", "/.well-known/acme-status/status.php", 200, 41, CURL),
    (at(2, 3, 51), ATTACKER2, "POST", "/.well-known/acme-status/status.php", 200, 563, CURL),
    (at(22, 17, 44, day=13), ATTACKER2, "POST", "/.well-known/acme-status/status.php", 200, 1207, CURL),
    (at(22, 18, 2, day=13), ATTACKER2, "GET", "/", 200, 1984, CURL),
]
for when, ip, method, path, status, size, ua in attack:
    add(when, ip, method, path, status, size, ua)

events.sort(key=lambda e: e[0])
for when, ip, method, path, status, size, ua, referer in events:
    if when >= END:
        continue
    stamp = when.strftime("%d/%b/%Y:%H:%M:%S %z")
    size_text = "-" if size == 0 else str(size)
    print(f'{ip} - - [{stamp}] "{method} {path} HTTP/1.1" {status} {size_text} "{referer}" "{ua}"')
