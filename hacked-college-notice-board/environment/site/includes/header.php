<?php $user = current_user(); ?>
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title><?= e($page_title ?? SITE_NAME) ?> - <?= e(SITE_NAME) ?></title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<header>
  <a class="brand" href="/"><?= e(SITE_NAME) ?> Notice Board</a>
  <nav>
    <?php if ($user): ?>
      <a href="/dashboard.php">Dashboard</a>
      <a href="/logout.php">Log out</a>
    <?php else: ?>
      <a href="/login.php">Staff login</a>
    <?php endif; ?>
  </nav>
</header>
<main>
