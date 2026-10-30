<?php
$db = new PDO('sqlite:' . $argv[1]);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
$stmt = $db->prepare('INSERT INTO users (username, full_name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)');
$stmt->execute(['it-support', 'IT Support', 'admin', password_hash('Upd@te-Sys-2026', PASSWORD_DEFAULT), '2026-10-12 01:41:09']);
