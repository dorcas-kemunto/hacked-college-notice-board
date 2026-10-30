#!/bin/bash
set -euo pipefail

SITE=/var/www/college.example.org
UP=$SITE/public/uploads

mkdir -p /root/evidence
keep() {
    for f in "$@"; do
        if [ -e "$f" ]; then cp -a --parents "$f" /root/evidence/; fi
    done
}

keep "$UP/2026/10/scan_0412.php"
rm -f "$UP/2026/10/scan_0412.php"

keep "$UP/staff-photo.jpg" "$UP/.htaccess" /etc/php/8.3/fpm/pool.d/www.conf
rm -f "$UP/staff-photo.jpg" "$UP/.htaccess"
sed -i 's/^security\.limit_extensions = .*/;security.limit_extensions = .php .php3 .php4 .php5 .php7/' \
    /etc/php/8.3/fpm/pool.d/www.conf

keep "$SITE/includes/footer.php"
sed -i '/_cfg_s/d' "$SITE/includes/footer.php"

keep "$SITE/public/.user.ini" /var/lib/php/sessions/.sess_lock
sed -i '/auto_prepend_file/d' "$SITE/public/.user.ini"
rm -f /var/lib/php/sessions/.sess_lock

keep /etc/apache2/conf-available/security-headers.conf /var/tmp/.font-cache
a2disconf -q security-headers
rm -f /etc/apache2/conf-available/security-headers.conf
rm -rf /var/tmp/.font-cache

sqlite3 "$SITE/database/college.sqlite" "DELETE FROM users WHERE username = 'it-support';"

keep /var/spool/cron/crontabs/www-data /var/www/.cache
rm -f /var/spool/cron/crontabs/www-data
rm -rf /var/www/.cache

keep /root/.ssh/authorized_keys
sed -i '/backup@college-srv/d' /root/.ssh/authorized_keys

keep /etc/passwd /etc/shadow
sed -i '/^sysbackup:/d' /etc/passwd /etc/shadow

cat > "$SITE/includes/functions.php" <<'PHP'
<?php
require_once __DIR__ . '/config.php';

session_start();

function db(): PDO
{
    static $pdo = null;
    if ($pdo === null) {
        $pdo = new PDO('sqlite:' . DB_PATH);
        $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        $pdo->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
    }
    return $pdo;
}

function e(?string $text): string
{
    return htmlspecialchars((string) $text, ENT_QUOTES, 'UTF-8');
}

function current_user(): ?array
{
    if (empty($_SESSION['user_id'])) {
        return null;
    }
    $stmt = db()->prepare('SELECT id, username, full_name, role FROM users WHERE id = ?');
    $stmt->execute([$_SESSION['user_id']]);
    $user = $stmt->fetch();
    return $user ?: null;
}

function require_login(): array
{
    $user = current_user();
    if ($user === null) {
        header('Location: /login.php');
        exit;
    }
    return $user;
}

function save_upload(array $file): ?string
{
    $allowed = ['pdf', 'jpg', 'jpeg', 'png', 'docx'];
    $ext = strtolower(pathinfo($file['name'], PATHINFO_EXTENSION));
    if (!in_array($ext, $allowed, true) || !is_uploaded_file($file['tmp_name'])) {
        return null;
    }
    $sub = date('Y') . '/' . date('m');
    $dir = UPLOAD_DIR . '/' . $sub;
    if (!is_dir($dir)) {
        mkdir($dir, 0775, true);
    }
    $name = bin2hex(random_bytes(8)) . '.' . $ext;
    if (!move_uploaded_file($file['tmp_name'], $dir . '/' . $name)) {
        return null;
    }
    return $sub . '/' . $name;
}
PHP

cat > "$SITE/public/upload.php" <<'PHP'
<?php
require __DIR__ . '/../includes/functions.php';

header('Content-Type: application/json');

if (current_user() === null) {
    http_response_code(403);
    echo json_encode(['error' => 'Please log in first.']);
    exit;
}

if (empty($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['error' => 'No file was sent.']);
    exit;
}

$path = save_upload($_FILES['file']);
if ($path === null) {
    http_response_code(415);
    echo json_encode(['error' => 'This type of file is not allowed.']);
    exit;
}
echo json_encode(['url' => '/uploads/' . $path]);
PHP

cat > "$SITE/public/post-notice.php" <<'PHP'
<?php
require __DIR__ . '/../includes/functions.php';

$user = require_login();
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = trim($_POST['title'] ?? '');
    $body = trim($_POST['body'] ?? '');
    $has_file = !empty($_FILES['attachment']) && $_FILES['attachment']['error'] === UPLOAD_ERR_OK;
    $path = $has_file ? save_upload($_FILES['attachment']) : null;

    if ($title === '' || $body === '') {
        $error = 'Title and text are both needed.';
    } elseif ($has_file && $path === null) {
        $error = 'Only PDF, JPG, PNG and DOCX files can be attached.';
    } else {
        $pdo = db();
        $stmt = $pdo->prepare('INSERT INTO notices (title, body, posted_by, created_at) VALUES (?, ?, ?, ?)');
        $stmt->execute([$title, $body, $user['id'], date('Y-m-d H:i:s')]);
        $notice_id = (int) $pdo->lastInsertId();

        if ($path !== null) {
            $stmt = $pdo->prepare(
                'INSERT INTO attachments (notice_id, original_name, stored_path, uploaded_at) VALUES (?, ?, ?, ?)'
            );
            $stmt->execute([$notice_id, basename($_FILES['attachment']['name']), $path, date('Y-m-d H:i:s')]);
        }

        header('Location: /notice.php?id=' . $notice_id);
        exit;
    }
}

$page_title = 'Post a notice';
require __DIR__ . '/../includes/header.php';
?>
<h1>Post a notice</h1>
<?php if ($error): ?><p class="error"><?= e($error) ?></p><?php endif; ?>
<form method="post" action="/post-notice.php" enctype="multipart/form-data">
  <label>Title <input name="title" required></label>
  <label>Text <textarea name="body" rows="8" required></textarea></label>
  <label>Attachment (optional) <input type="file" name="attachment"></label>
  <button type="submit">Post notice</button>
</form>
<?php require __DIR__ . '/../includes/footer.php'; ?>
PHP

cat > /etc/apache2/sites-available/college.example.org.conf <<'CONF'
<VirtualHost *:80>
    ServerName college.example.org
    ServerAdmin ict@college.example.org
    DocumentRoot /var/www/college.example.org/public

    <Directory /var/www/college.example.org/public>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
    </Directory>

    <Directory /var/www/college.example.org/public/uploads>
        AllowOverride None
        <FilesMatch "\.(php[0-9]?|phtml|phar)$">
            Require all denied
        </FilesMatch>
    </Directory>

    <FilesMatch "\.php$">
        SetHandler "proxy:unix:/run/php/php8.3-fpm.sock|fcgi://localhost"
    </FilesMatch>

    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
CONF

php-fpm8.3 -t
apachectl configtest
service php8.3-fpm restart
service apache2 restart
sleep 1
bash /root/handover/site-check.sh
