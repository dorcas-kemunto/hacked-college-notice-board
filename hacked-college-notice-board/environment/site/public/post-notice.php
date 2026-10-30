<?php
require __DIR__ . '/../includes/functions.php';

$user = require_login();
$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $title = trim($_POST['title'] ?? '');
    $body = trim($_POST['body'] ?? '');
    if ($title === '' || $body === '') {
        $error = 'Title and text are both needed.';
    } else {
        $pdo = db();
        $stmt = $pdo->prepare('INSERT INTO notices (title, body, posted_by, created_at) VALUES (?, ?, ?, ?)');
        $stmt->execute([$title, $body, $user['id'], date('Y-m-d H:i:s')]);
        $notice_id = (int) $pdo->lastInsertId();

        if (!empty($_FILES['attachment']) && $_FILES['attachment']['error'] === UPLOAD_ERR_OK) {
            $path = save_upload($_FILES['attachment']);
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
