<?php
require __DIR__ . '/../includes/functions.php';

header('Content-Type: application/json');

if (empty($_FILES['file']) || $_FILES['file']['error'] !== UPLOAD_ERR_OK) {
    http_response_code(400);
    echo json_encode(['error' => 'No file was sent.']);
    exit;
}

$path = save_upload($_FILES['file']);
echo json_encode(['url' => '/uploads/' . $path]);
