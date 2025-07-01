
<?php
$data = json_decode(file_get_contents('php://input'), true);
$log = "log.txt";
file_put_contents($log, json_encode($data, JSON_PRETTY_PRINT) . "\n", FILE_APPEND);
?>
