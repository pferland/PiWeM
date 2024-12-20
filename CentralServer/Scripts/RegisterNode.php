<?php
/**
 * Created by PhpStorm.
 * User: pferland
 * Date: 10/26/2016
 * Time: 4:49 PM
 */

$lib_path = getenv("PiWem_Home")."/lib/";
include $lib_path."SQL.php";
include $lib_path."config.php";

$short_opts = "";

$long_opts = array(
    "station_name:",
    "station_hash:"
);

$options = getopt($short_opts, $long_opts);

$sql = new SQL($WWWconfig['SQL']);

$timestamp = date("Y-m-d H:i:s");

$station_name = $options['station_name'];
$station_hash = $options['station_hash'];
$station_key = base64_encode(microtime().rand()); // Don't know why I was using that stupidly complex function before...

$timestamp = date("Y-m-d H:i:s");
var_dump($timestamp);
$prep = $sql->conn->prepare("INSERT INTO `weather_data`.`Stations` ( station_name, station_hash, station_key, `timestamp`) VALUES (?, ?, ?, ?)");
$prep->bindParam(1, $station_name, PDO::PARAM_STR);
$prep->bindParam(2, $station_hash, PDO::PARAM_STR);
$prep->bindParam(3, $station_key, PDO::PARAM_STR);
$prep->bindParam(4, $timestamp, PDO::PARAM_STR);
$prep->execute();

echo "Station ".$station_name." has the following key assigned to it: ".$station_key."\r\n";
echo "Done!\r\n";
