#!/bin/bash
BASE=http://127.0.0.1
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT
JAR="$WORK/cookies"
failed=0

ok()  { echo "OK    $1"; }
bad() { echo "FAIL  $1"; failed=1; }

home=$(curl -s "$BASE/")
for title in "Second Term Opening Dates" "Fees Structure for 2026/2027" \
             "Library Opening Hours During Exams" "Teaching Practice Allocation" \
             "Sports Day Photos" "Collection of End of Term Results"; do
    if grep -qF "$title" <<<"$home"; then ok "home page shows: $title"; else bad "home page shows: $title"; fi
done
if grep -qF "P.O. Box 100" <<<"$home"; then ok "footer shows"; else bad "footer shows"; fi

check_attachment() {
    local id=$1 name=$2 sum=$3 page href got
    page=$(curl -s "$BASE/notice.php?id=$id")
    href=$(grep -o "<a href=\"[^\"]*\">$name</a>" <<<"$page" | head -n 1 | sed 's/^<a href="\([^"]*\)".*/\1/')
    if [ -z "$href" ]; then bad "notice $id links $name"; return; fi
    href=${href//&amp;/&}
    got=$(curl -s "$BASE$href" | sha256sum | cut -d' ' -f1)
    if [ "$got" = "$sum" ]; then ok "$name downloads unchanged"; else bad "$name downloads unchanged"; fi
}
check_attachment 1 term-dates-2026.pdf 963afdf981d3f490e7a0e33204d72aeb0c48ded74ae8f2bd07b1f73d3f5135fd
check_attachment 2 fees-structure-2026-2027.pdf f7fd64120e561e22933edf7c5ca75ef266bac28c8bc2f49fa5081210c1e4b320
check_attachment 4 tp-allocation-2026.docx 1684e313ae6f87458a4f7cb3cb8fa4d0736a5a3d464cb03a092891fd9effee62
check_attachment 5 sports-day-2026.jpg 7235ce9329e824f3099ff6c5e4ff3a09dba0d676f6e9f14c1cc873ddef9c2d27

curl -s -c "$JAR" -b "$JAR" -o /dev/null "$BASE/login.php"
curl -s -c "$JAR" -b "$JAR" -o /dev/null --data-urlencode "username=registrar" \
     --data-urlencode "password=Registrar#2026" "$BASE/login.php"
if curl -s -c "$JAR" -b "$JAR" "$BASE/dashboard.php" | grep -q "registrar"; then
    ok "registrar can log in"
else
    bad "registrar can log in"
fi

base64 -d > "$WORK/check.png" <<'PNG'
iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==
PNG
answer=$(curl -s -c "$JAR" -b "$JAR" -F "file=@$WORK/check.png;type=image/png" "$BASE/upload.php")
url=$(python3 -c 'import json,sys; print(json.loads(sys.stdin.read()).get("url",""))' <<<"$answer" 2>/dev/null)
if [ -n "$url" ] && curl -s "$BASE$url" | cmp -s - "$WORK/check.png"; then
    ok "upload.php takes a PNG and gives it back"
else
    bad "upload.php takes a PNG and gives it back"
fi

if [ "$failed" -eq 0 ]; then echo "All site checks passed."; else echo "Some site checks failed."; fi
exit "$failed"
