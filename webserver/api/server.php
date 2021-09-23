<?php
$token = $_GET["token"];
$do = $_GET["do"];
$data = $_GET["data"];

if ($token != "API_TOKEN") {
    echo "Invalid access token";
    http_response_code(401);
    return;
}

header('Content-Type: application/json; charset=utf-8');

if ($do == "getdb") {
    $file = "../database.json";
    $data = file_get_contents($file);
    echo $data;
    http_response_code(200);
    return;
}

if ($do == "setdb") {
    $file = "../database.json";
    file_put_contents($file, $data);
    http_response_code(200);
    return;
}

if ($do == "getPatterns") {
    $file = "../patterns.json";
    $data = file_get_contents($file);
    echo $data;
    http_response_code(200);
    return;
}

if ($do == "setPatterns") {
    $file = "../patterns.json";
    file_put_contents($file, $data);
    http_response_code(200);
    return;
}

if ($do == "getEB") {
    $file = "../embeds_blacklist.json";
    $data = file_get_contents($file);
    echo $data;
    http_response_code(200);
    return;
}

if ($do == "setEB") {
    $file = "../embeds_blacklist.json";
    file_put_contents($file, $data);
    http_response_code(200);
    return;
}

if ($do == "setSession") {
    $file = "../session.json";
    file_put_contents($file, $data);
    http_response_code(200);
    return;
}

if ($do == "setStats") {
    $file = "../stats.json";
    file_put_contents($file, $data);
    http_response_code(200);
    return;
}
?>
