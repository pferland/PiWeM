<?php
/**
 * Created by PhpStorm.
 * User: pferland
 * Date: 10/26/2016
 * Time: 4:49 PM
 */

include "config.php";
include $config['Lib_Path']."SQL.php";
include $config['Lib_Path']."config.php";

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
$station_key = v4();

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



function v4() {
    return sprintf('%04x%04x-%04x-%04x-%04x-%04x%04x%04x',

        // 32 bits for "time_low"
        mt_rand(0, 0xffff), mt_rand(0, 0xffff),

        // 16 bits for "time_mid"
        mt_rand(0, 0xffff),

        // 16 bits for "time_hi_and_version",
        // four most significant bits holds version number 4
        mt_rand(0, 0x0fff) | 0x4000,

        // 16 bits, 8 bits for "clk_seq_hi_res",
        // 8 bits for "clk_seq_low",
        // two most significant bits holds zero and one for variant DCE1.1
        mt_rand(0, 0x3fff) | 0x8000,

        // 48 bits for "node"
        mt_rand(0, 0xffff), mt_rand(0, 0xffff), mt_rand(0, 0xffff)
    );
}
