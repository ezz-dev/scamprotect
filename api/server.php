<?php
$token = $_GET["token"];
$do = $_GET["do"];
$data = $_GET["data"];

if($token != "API_TOKEN") {
  http_response_code(401);
  return;
}

if($do == "getdb") {
  $file = "database.json";
  $data = file_get_contents($file);
  http_response_code(200);
  echo $data
}

if($do == "setdb") {
  $file = "database.json";
  file_put_contents($file, $data);
  http_response_code(200);
}
?>
