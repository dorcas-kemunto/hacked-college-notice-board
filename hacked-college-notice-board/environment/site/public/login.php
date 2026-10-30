<?php
require __DIR__ . '/../includes/functions.php';

$error = '';
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $stmt = db()->prepare('SELECT id, password_hash FROM users WHERE username = ?');
    $stmt->execute([trim($_POST['username'] ?? '')]);
    $row = $stmt->fetch();
    if ($row && password_verify($_POST['password'] ?? '', $row['password_hash'])) {
        session_regenerate_id(true);
        $_SESSION['user_id'] = $row['id'];
        header('Location: /dashboard.php');
        exit;
    }
    $error = 'Wrong username or password.';
}

$page_title = 'Staff login';
require __DIR__ . '/../includes/header.php';
?>
<h1>Staff login</h1>
<?php if ($error): ?><p class="error"><?= e($error) ?></p><?php endif; ?>
<form method="post" action="/login.php">
  <label>Username <input name="username" required></label>
  <label>Password <input name="password" type="password" required></label>
  <button type="submit">Log in</button>
</form>
<?php require __DIR__ . '/../includes/footer.php'; ?>
