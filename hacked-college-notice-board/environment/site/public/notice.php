<?php
require __DIR__ . '/../includes/functions.php';

$id = (int) ($_GET['id'] ?? 0);
$stmt = db()->prepare(
    'SELECT n.*, u.full_name FROM notices n JOIN users u ON u.id = n.posted_by WHERE n.id = ?'
);
$stmt->execute([$id]);
$notice = $stmt->fetch();

if (!$notice) {
    http_response_code(404);
    $page_title = 'Notice not found';
    require __DIR__ . '/../includes/header.php';
    echo '<h1>Notice not found</h1>';
    require __DIR__ . '/../includes/footer.php';
    exit;
}

$files = db()->prepare('SELECT original_name, stored_path FROM attachments WHERE notice_id = ? ORDER BY id');
$files->execute([$id]);
$attachments = $files->fetchAll();

$page_title = $notice['title'];
require __DIR__ . '/../includes/header.php';
?>
<h1><?= e($notice['title']) ?></h1>
<p class="meta">Posted <?= e(date('j M Y', strtotime($notice['created_at']))) ?> by <?= e($notice['full_name']) ?></p>
<div class="body"><?= nl2br(e($notice['body'])) ?></div>
<?php if ($attachments): ?>
<h2>Attachments</h2>
<ul class="attachments">
<?php foreach ($attachments as $a): ?>
  <li><a href="/uploads/<?= e($a['stored_path']) ?>"><?= e($a['original_name']) ?></a></li>
<?php endforeach; ?>
</ul>
<?php endif; ?>
<?php require __DIR__ . '/../includes/footer.php'; ?>
