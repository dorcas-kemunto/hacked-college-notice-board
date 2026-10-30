<?php
$db = new PDO('sqlite:' . $argv[1]);
$db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

$db->exec('CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL
)');
$db->exec('CREATE TABLE notices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    posted_by INTEGER NOT NULL REFERENCES users(id),
    created_at TEXT NOT NULL
)');
$db->exec('CREATE TABLE attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    notice_id INTEGER NOT NULL REFERENCES notices(id),
    original_name TEXT NOT NULL,
    stored_path TEXT NOT NULL,
    uploaded_at TEXT NOT NULL
)');

$users = [
    ['ict.officer', 'Grace Nanjala', 'admin', 'Nanjala!ICT24', '2026-01-15 09:20:00'],
    ['registrar', 'Mary Achieng', 'staff', 'Registrar#2026', '2026-01-15 09:31:00'],
    ['dean.students', 'Peter Ekal', 'staff', 'Kerio-Dean-77', '2026-02-03 11:05:00'],
];
$stmt = $db->prepare('INSERT INTO users (username, full_name, role, password_hash, created_at) VALUES (?, ?, ?, ?, ?)');
foreach ($users as [$username, $name, $role, $password, $created]) {
    $stmt->execute([$username, $name, $role, password_hash($password, PASSWORD_DEFAULT), $created]);
}

$notices = [
    [1, 'Second Term Opening Dates', "Second term starts in September. The dates for each year are in the attached letter.\nAll fees must be cleared before registration.", 2, '2026-09-01 08:30:00'],
    [2, 'Fees Structure for 2026/2027', "The fees structure for the 2026/2027 year is attached.\nPay through the college bank account only. Cash is not accepted at the office.", 2, '2026-09-08 09:10:00'],
    [3, 'Library Opening Hours During Exams', "During the end of term exams the library will open from 7:00 a.m. to 10:00 p.m., Monday to Saturday.\nPlease keep the reading rooms quiet.", 3, '2026-09-15 15:45:00'],
    [4, 'Teaching Practice Allocation', "Second year students can find their teaching practice schools in the attached list.\nReport to your school on Monday 12 October 2026.", 2, '2026-09-22 14:05:00'],
    [5, 'Sports Day Photos', "Thank you to everyone who took part in sports day. Some photos are attached.", 3, '2026-10-03 16:40:00'],
    [6, 'Collection of End of Term Results', "Result slips can be collected from the exams office from Monday 19 October 2026.\nBring your college ID.", 2, '2026-10-09 10:12:00'],
];
$stmt = $db->prepare('INSERT INTO notices (id, title, body, posted_by, created_at) VALUES (?, ?, ?, ?, ?)');
foreach ($notices as $n) {
    $stmt->execute($n);
}

$attachments = [
    [1, 'term-dates-2026.pdf', '2026/09/term-dates-2026.pdf', '2026-09-01 08:30:00'],
    [2, 'fees-structure-2026-2027.pdf', '2026/09/fees-structure-2026-2027.pdf', '2026-09-08 09:10:00'],
    [4, 'tp-allocation-2026.docx', '2026/09/tp-allocation-2026.docx', '2026-09-22 14:05:00'],
    [5, 'sports-day-2026.jpg', '2026/10/sports-day-2026.jpg', '2026-10-03 16:40:00'],
];
$stmt = $db->prepare('INSERT INTO attachments (notice_id, original_name, stored_path, uploaded_at) VALUES (?, ?, ?, ?)');
foreach ($attachments as $a) {
    $stmt->execute($a);
}
