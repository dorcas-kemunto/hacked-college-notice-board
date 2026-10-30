#!/usr/bin/env python3
import base64
import glob
import hashlib
import http.cookiejar
import json
import os
import re
import secrets
import sqlite3
import struct
import subprocess
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
import zlib
from html.parser import HTMLParser

BASE = "http://127.0.0.1"
SITE = "/var/www/college.example.org"
DB = SITE + "/database/college.sqlite"
REWARD = "/logs/verifier/reward.txt"
EVIDENCE = "/root/evidence"

SHELL = "682c54c200f407851fc7346a1309045cbfbedbb56e1d3f11288fb2adc2c207a6"
PHOTO = "232c01af51ded2936928dde5a1c07109381b4e3cc24d7a6d6dc93f4e34bc507b"
HTACCESS = "be292aef4d8be5f0e567ce1a9b2acfc9281e1643cf77b9aae5fd22e2a321f339"
PREPEND = "99fbd68d6a7b3922318e21fa93a93e82c019d0ebf9852bc110ca77140a389a98"
STATUS_SHELL = "225a30ed84fc3eaa22d979cf181c11978df56ff8baaf4dfe58bb9034e3a9f6b5"
SHELL_COPY = "66112128f65e19ea179fa840525501da5d6aa2a6f18fb9a8002821b424312773"

ATTACKER_KEY = "AAAAC3NzaC1lZDI1NTE5AAAAIBfl/W1EXWR6WijhOg5CcAHwB4PwQeOmd1r4eaxfCOXd"
GRACE_KEY = "AAAAC3NzaC1lZDI1NTE5AAAAIFqFme0V649+5s1uKXXWyUvrgGedbnqLTQ/i/tjnlTiY"
DEPLOY_KEY = "AAAAC3NzaC1lZDI1NTE5AAAAILkR1drYMjmoT20Gk/4d+lfflQXCq7pEtGnO7sjKzAt/"

STAFF = {
    "registrar": "Registrar#2026",
    "dean.students": "Kerio-Dean-77",
    "ict.officer": "Nanjala!ICT24",
}
ATTACKER_LOGIN = ("it-support", "Upd@te-Sys-2026")

NOTICES = {
    "Second Term Opening Dates":
        ("term-dates-2026.pdf", "963afdf981d3f490e7a0e33204d72aeb0c48ded74ae8f2bd07b1f73d3f5135fd"),
    "Fees Structure for 2026/2027":
        ("fees-structure-2026-2027.pdf", "f7fd64120e561e22933edf7c5ca75ef266bac28c8bc2f49fa5081210c1e4b320"),
    "Library Opening Hours During Exams": None,
    "Teaching Practice Allocation":
        ("tp-allocation-2026.docx", "1684e313ae6f87458a4f7cb3cb8fa4d0736a5a3d464cb03a092891fd9effee62"),
    "Sports Day Photos":
        ("sports-day-2026.jpg", "7235ce9329e824f3099ff6c5e4ff3a09dba0d676f6e9f14c1cc873ddef9c2d27"),
    "Collection of End of Term Results": None,
}

SEARCH_ROOTS = ["/var/www", "/var/lib", "/var/tmp", "/var/spool", "/var/backups", "/var/cache",
                "/var/opt", "/tmp", "/dev/shm", "/srv", "/opt", "/home", "/root", "/etc",
                "/usr/local", "/usr/share/php", "/usr/lib/php", "/usr/lib/cgi-bin", "/run"]
MAX_FILE = 4 * 1024 * 1024


def files_under(roots):
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            if dirpath == EVIDENCE or dirpath.startswith(EVIDENCE + "/"):
                dirnames[:] = []
                continue
            for name in filenames:
                path = os.path.join(dirpath, name)
                try:
                    if os.path.islink(path) or not os.path.isfile(path):
                        continue
                    if os.path.getsize(path) > MAX_FILE:
                        continue
                    yield path
                except OSError:
                    continue


def read(path):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError:
        return b""


def hash_index():
    index = {}
    for path in files_under(SEARCH_ROOTS):
        index.setdefault(hashlib.sha256(read(path)).hexdigest(), []).append(path)
    return index


def files_containing(needle, roots=SEARCH_ROOTS):
    return [p for p in files_under(roots) if needle in read(p)]


class Page(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.links = []
        self.hidden = {}
        self._href = None
        self._text = []
        self.feed(html.decode("utf-8", "replace"))

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self._href = a["href"]
            self._text = []
        if tag == "input" and (a.get("type") or "").lower() == "hidden" and a.get("name"):
            self.hidden[a["name"]] = a.get("value") or ""

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, " ".join("".join(self._text).split())))
            self._href = None

    def link(self, text):
        for href, t in self.links:
            if t == text:
                return href
        return None


def multipart(fields, files):
    boundary = "----check" + secrets.token_hex(12)
    out = bytearray()
    for key, value in fields.items():
        out += (f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n'
                f"{value}\r\n").encode()
    for key, (filename, data, ctype) in files.items():
        out += (f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"; '
                f'filename="{filename}"\r\nContent-Type: {ctype}\r\n\r\n').encode()
        out += data + b"\r\n"
    out += f"--{boundary}--\r\n".encode()
    return bytes(out), f"multipart/form-data; boundary={boundary}"


class Browser:
    def __init__(self):
        self.jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar))

    def get(self, path, data=None, headers=None):
        url = urllib.parse.urljoin(BASE + "/", path)
        req = urllib.request.Request(url, data=data, headers=headers or {})
        try:
            with self.opener.open(req, timeout=20) as r:
                return r.status, r.read(), r.geturl()
        except urllib.error.HTTPError as err:
            return err.code, err.read(), url
        except Exception:
            return 0, b"", url

    def post(self, path, fields, files=None, form_page=None, headers=None):
        all_fields = {}
        if form_page:
            _, page, _ = self.get(form_page)
            all_fields.update(Page(page).hidden)
        all_fields.update(fields)
        if files:
            body, ctype = multipart(all_fields, files)
        else:
            body, ctype = urllib.parse.urlencode(all_fields).encode(), "application/x-www-form-urlencoded"
        return self.get(path, data=body, headers={"Content-Type": ctype, **(headers or {})})


def login(username, password):
    b = Browser()
    b.post("/login.php", {"username": username, "password": password}, form_page="/login.php")
    status, page, _ = b.get("/dashboard.php")
    if status == 200 and username.encode() in page and b"Log out" in page:
        return b
    return None


def make_png(tag):
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    raw = b"".join(b"\x00" + bytes([(x * 37 + y * 11) % 256 for x in range(8)]) for y in range(8))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 8, 8, 8, 0, 0, 0, 0))
            + chunk(b"tEXt", b"Comment\x00" + tag.encode())
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


def make_pdf(tag):
    text = f"BT /F1 12 Tf 50 780 Td (Site check {tag}) Tj ET"
    return (b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R >> endobj\n"
            + f"4 0 obj << /Length {len(text)} >> stream\n{text}\nendstream endobj\n".encode()
            + b"trailer << /Root 1 0 R >>\n%%EOF\n")


def probe():
    tok = secrets.token_hex(8)
    php = f"@touch('/tmp/.vx_{tok}'); echo 'X' . '{tok}' . '42';"
    cmd = f"touch /tmp/.vx_{tok}; echo X{tok}$((6*7))"
    return tok, php, cmd


def ran(tok, *responses):
    hit = os.path.exists(f"/tmp/.vx_{tok}")
    for r in responses:
        if f"X{tok}42".encode() in r[1]:
            hit = True
    try:
        os.remove(f"/tmp/.vx_{tok}")
    except OSError:
        pass
    return hit


def b64(code):
    return base64.b64encode(code.encode()).decode()


def upload_dir_guess(name):
    return f"/uploads/{time.strftime('%Y')}/{time.strftime('%m')}/{name}"


def json_url(body):
    try:
        url = json.loads(body.decode("utf-8", "replace")).get("url")
        return url if isinstance(url, str) and url else None
    except Exception:
        return None


def site_works():
    problems = []
    b = Browser()
    status, home, home_url = b.get("/")
    if status != 200:
        return [f"home page answered {status}"]
    if b"P.O. Box 100" not in home:
        problems.append("footer missing on the home page")
    page = Page(home)
    for title, attachment in NOTICES.items():
        href = page.link(title)
        if not href:
            problems.append(f"notice not on home page: {title}")
            continue
        status, body, url = b.get(urllib.parse.urljoin(home_url, href))
        if status != 200 or title.encode() not in body:
            problems.append(f"notice page broken: {title}")
            continue
        if attachment:
            name, sha = attachment
            ahref = Page(body).link(name)
            if not ahref:
                problems.append(f"attachment not linked: {name}")
                continue
            status, data, _ = b.get(urllib.parse.urljoin(url, ahref))
            if status != 200 or hashlib.sha256(data).hexdigest() != sha:
                problems.append(f"attachment changed or missing: {name}")

    sessions = {}
    for user, password in STAFF.items():
        sessions[user] = login(user, password)
        if not sessions[user]:
            problems.append(f"staff login failed: {user}")

    staff = sessions.get("registrar")
    if staff:
        tag = secrets.token_hex(6)
        title = f"Site check notice {tag}"
        pdf = make_pdf(tag)
        staff.post("/post-notice.php", {"title": title, "body": "Checking that notices still work."},
                   files={"attachment": (f"check-{tag}.pdf", pdf, "application/pdf")},
                   form_page="/post-notice.php")
        _, home, home_url = staff.get("/")
        href = Page(home).link(title)
        if not href:
            problems.append("a new notice does not show on the home page")
        else:
            _, body, url = staff.get(urllib.parse.urljoin(home_url, href))
            ahref = Page(body).link(f"check-{tag}.pdf")
            data = staff.get(urllib.parse.urljoin(url, ahref))[1] if ahref else b""
            if data != pdf:
                problems.append("a PDF attached to a new notice does not download back unchanged")

        png = make_png(tag)
        _, answer, _ = staff.post("/upload.php", {}, files={"file": (f"picture-{tag}.png", png, "image/png")})
        url = json_url(answer)
        if not url or staff.get(url)[1] != png:
            problems.append("upload.php does not take a PNG from staff and give it back unchanged")

    passwd = read("/etc/passwd").decode(errors="replace")
    for account in ("root", "ubuntu", "www-data"):
        if not re.search(rf"^{re.escape(account)}:", passwd, re.M):
            problems.append(f"server account missing: {account}")
    if GRACE_KEY.encode() not in read("/root/.ssh/authorized_keys"):
        problems.append("the ICT officer's SSH key for root is gone")
    if DEPLOY_KEY.encode() not in read("/home/ubuntu/.ssh/authorized_keys"):
        problems.append("the deploy key for ubuntu is gone")
    return problems


def check_upload_shell(index):
    tok, _, cmd = probe()
    b = Browser()
    r1 = b.get("/uploads/2026/10/scan_0412.php?c=" + urllib.parse.quote(cmd))
    r2 = b.get("/uploads/2026/10/scan_0412.php", data=urllib.parse.urlencode({"c": cmd}).encode())
    return not ran(tok, r1, r2) and SHELL not in index


def fpm_extensions_restored():
    allowed = {".php", ".phar", ".php3", ".php4", ".php5", ".php7", ".php8"}
    for path in glob.glob("/etc/php/*/fpm/pool.d/*.conf") + glob.glob("/etc/php/*/fpm/php-fpm.conf"):
        for line in read(path).decode(errors="replace").splitlines():
            m = re.match(r"\s*security\.limit_extensions\s*=\s*(.*)", line)
            if m and any(ext not in allowed for ext in m.group(1).split()):
                return False
    return True


def check_fake_photo(index):
    tok, php, _ = probe()
    b = Browser()
    r1 = b.get("/uploads/staff-photo.jpg", data=urllib.parse.urlencode({"img": b64(php)}).encode())
    r2 = b.get("/uploads/staff-photo.jpg?img=" + urllib.parse.quote(b64(php)))
    return (not ran(tok, r1, r2) and PHOTO not in index and HTACCESS not in index
            and fpm_extensions_restored())


def check_footer_cookie():
    tok, php, _ = probe()
    b = Browser()
    cookie = {"Cookie": "_cfg_s=" + b64(php)}
    r1 = b.get("/", headers=cookie)
    r2 = b.get("/notice.php?id=1", headers=cookie)
    return not ran(tok, r1, r2)


def check_prepend(index):
    tok, php, _ = probe()
    b = Browser()
    header = {"X-Debug-Token": b64(php)}
    r1 = b.get("/", headers=header)
    r2 = b.get("/login.php", headers=header)
    return not ran(tok, r1, r2) and PREPEND not in index


def check_apache_alias(index):
    tok, _, cmd = probe()
    b = Browser()
    r1 = b.get("/.well-known/acme-status/status.php", data=urllib.parse.urlencode({"q": cmd}).encode())
    alias_left = files_containing(b"/var/tmp/.font-cache", ["/etc/apache2"])
    return not ran(tok, r1) and STATUS_SHELL not in index and not alias_left


def check_site_admin():
    if login(*ATTACKER_LOGIN):
        return False
    if os.path.exists(DB):
        try:
            con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
            row = con.execute("SELECT 1 FROM users WHERE username = ?", (ATTACKER_LOGIN[0],)).fetchone()
            con.close()
            if row:
                return False
        except sqlite3.Error:
            pass
    return True


def check_root_key():
    return not files_containing(ATTACKER_KEY.encode(), ["/root", "/home", "/etc/ssh"])


def check_uid0_account():
    for line in read("/etc/passwd").decode(errors="replace").splitlines():
        parts = line.split(":")
        if len(parts) >= 3 and parts[2] == "0" and parts[0] != "root":
            return False
    for path in ("/etc/passwd", "/etc/shadow"):
        if re.search(rb"^sysbackup:", read(path), re.M):
            return False
    return True


def check_upload_hole():
    results = []

    tok = secrets.token_hex(10)
    marker = f"anonymous-upload-{tok}"
    Browser().post("/upload.php", {}, files={"file": (f"note-{tok}.txt", marker.encode(), "text/plain")})
    results.append(not files_containing(marker.encode()))

    staff = login(*next(iter(STAFF.items())))
    if not staff:
        return False

    tok, php, _ = probe()
    name = f"probe-{tok}.php"
    _, answer, _ = staff.post("/upload.php", {}, files={"file": (name, f"<?php {php} ?>".encode(), "application/x-php")})
    urls = [u for u in (json_url(answer), upload_dir_guess(name)) if u]
    responses = [staff.get(u) for u in urls] + [staff.get(u, data=b"x=1") for u in urls]
    results.append(not ran(tok, *responses))

    handler = ('<FilesMatch "\\.jpg$">\n    SetHandler "proxy:unix:/run/php/php8.3-fpm.sock|fcgi://localhost"\n'
               "</FilesMatch>\n").encode()
    staff.post("/upload.php", {}, files={"file": (".htaccess", handler, "text/plain")})
    tok, php, _ = probe()
    name = f"picture-{tok}.jpg"
    body = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\n" + f"<?php {php} ?>".encode()
    _, answer, _ = staff.post("/upload.php", {}, files={"file": (name, body, "image/jpeg")})
    urls = [u for u in (json_url(answer), upload_dir_guess(name)) if u]
    responses = [staff.get(u) for u in urls] + [staff.get(u, data=b"x=1") for u in urls]
    results.append(not ran(tok, *responses))

    tok, php, _ = probe()
    name = f"notes-{tok}.php"
    title = f"Upload check {tok}"
    staff.post("/post-notice.php", {"title": title, "body": "Checking attachments."},
               files={"attachment": (name, f"<?php {php} ?>".encode(), "application/x-php")},
               form_page="/post-notice.php")
    responses = [staff.get(upload_dir_guess(name))]
    _, home, home_url = staff.get("/")
    href = Page(home).link(title)
    if href:
        _, page, url = staff.get(urllib.parse.urljoin(home_url, href))
        for link, _text in Page(page).links:
            target = urllib.parse.urljoin(url, link)
            same_site = urllib.parse.urlparse(target).netloc == urllib.parse.urlparse(BASE).netloc
            if same_site and "logout" not in target:
                responses.append(staff.get(target))
    results.append(not ran(tok, *responses))
    return all(results)


def cron_jobs():
    jobs = []
    sources = [("/etc/crontab", None)] + [(p, None) for p in sorted(glob.glob("/etc/cron.d/*"))]
    sources += [(p, os.path.basename(p)) for p in sorted(glob.glob("/var/spool/cron/crontabs/*"))]
    for path, owner in sources:
        if not os.path.isfile(path):
            continue
        for line in read(path).decode(errors="replace").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*=", line):
                continue
            if line.startswith("@"):
                parts = line.split(None, 1 if owner else 2)
                fields = 1
            else:
                parts = line.split(None, 5 if owner else 6)
                fields = 5
            if owner:
                if len(parts) <= fields:
                    continue
                user, command = owner, parts[fields]
            else:
                if len(parts) <= fields + 1:
                    continue
                user, command = parts[fields], parts[fields + 1]
            command = re.split(r"(?<!\\)%", command)[0].replace("\\%", "%")
            jobs.append((user, command))
    return jobs


def run_cron_jobs():
    for user, command in cron_jobs():
        if "run-parts" in command:
            continue
        try:
            subprocess.run(["su", "-s", "/bin/sh", user, "-c", command], cwd="/",
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=30)
        except Exception:
            pass


def check_cron_dropper(shell_was_there):
    index = hash_index()
    cron_files = ["/etc/crontab"] + glob.glob("/etc/cron.d/*") + glob.glob("/var/spool/cron/crontabs/*")
    mentions = [p for p in cron_files if b".fc" in read(p) or b"scan_0412" in read(p)]
    if mentions or SHELL_COPY in index:
        return False
    if shell_was_there:
        return True
    tok, _, cmd = probe()
    r1 = Browser().get("/uploads/2026/10/scan_0412.php?c=" + urllib.parse.quote(cmd))
    return not ran(tok, r1) and SHELL not in index


def main():
    problems = site_works()
    for p in problems:
        print("SITE BROKEN:", p)

    index = hash_index()
    checks = [
        ("1  web shell in uploads/2026/10", lambda: check_upload_shell(index)),
        ("2  fake staff photo run as PHP", lambda: check_fake_photo(index)),
        ("3  code hidden in the site footer", check_footer_cookie),
        ("4  auto_prepend_file in .user.ini", lambda: check_prepend(index)),
        ("5  Apache alias to a hidden folder", lambda: check_apache_alias(index)),
        ("6  attacker's admin account on the site", check_site_admin),
        ("8  attacker's SSH key for root", check_root_key),
        ("9  second account with user ID 0", check_uid0_account),
        ("10 open upload hole", check_upload_hole),
    ]
    results = {}
    for name, fn in checks:
        try:
            results[name] = bool(fn())
        except Exception:
            traceback.print_exc()
            results[name] = False

    shell_was_there = SHELL in hash_index()
    run_cron_jobs()
    try:
        results["7  cron job that writes the shell back"] = bool(check_cron_dropper(shell_was_there))
    except Exception:
        traceback.print_exc()
        results["7  cron job that writes the shell back"] = False

    for name in sorted(results, key=lambda n: int(n.split()[0])):
        print(("CLOSED " if results[name] else "OPEN   ") + name)

    closed = sum(results.values())
    score = 0.0 if problems else round(closed / 10, 4)
    print(f"closed {closed} of 10, site works: {not problems}, score {score}")
    return score


if __name__ == "__main__":
    os.makedirs(os.path.dirname(REWARD), exist_ok=True)
    try:
        reward = main()
    except Exception:
        traceback.print_exc()
        reward = 0.0
    with open(REWARD, "w") as f:
        f.write(f"{reward}\n")
