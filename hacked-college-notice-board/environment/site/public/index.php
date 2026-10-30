<?php
require __DIR__ . '/../includes/functions.php';

$page_title = 'Notices';
$notices = db()->query(
    'SELECT n.id, n.title, n.created_at, u.full_name
       FROM notices n JOIN users u ON u.id = n.posted_by
      ORDER BY n.created_at DESC, n.id DESC'
)->fetchAll();

require __DIR__ . '/../includes/header.php';
?>
<h1>Notices</h1>
<ul class="notices">
<?php foreach ($notices as $n): ?>
  <li>
    <a href="/notice.php?id=<?= (int) $n['id'] ?>"><?= e($n['title']) ?></a>
    <span class="meta"><?= e(date('j M Y', strtotime($n['created_at']))) ?> &middot; <?= e($n['full_name']) ?></span>
  </li>
<?php endforeach; ?>
</ul>
<?php require __DIR__ . '/../includes/footer.php'; ?>
