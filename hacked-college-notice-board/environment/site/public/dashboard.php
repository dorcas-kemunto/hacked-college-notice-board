<?php
require __DIR__ . '/../includes/functions.php';

$user = require_login();
$page_title = 'Dashboard';
require __DIR__ . '/../includes/header.php';
?>
<h1>Dashboard</h1>
<p>Logged in as <strong><?= e($user['username']) ?></strong> (<?= e($user['full_name']) ?>).</p>
<p><a href="/post-notice.php">Post a new notice</a></p>
<?php require __DIR__ . '/../includes/footer.php'; ?>
