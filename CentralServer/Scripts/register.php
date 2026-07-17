#!/usr/bin/env php
<?php

// 1. Define help configuration and parse arguments first
$shortopts  = "n:t:huk:";
$longopts  = array(
    "name:",
    "hash:",
    "type:",
    "help",
    "update",
    "key:",
);
$options = getopt($shortopts, $longopts);

if (isset($options['h']) || isset($options['help'])) {
    echo "PiWeM Registration Tool\n\n";
    echo "Usage:\n";
    echo "  ./register.php -n <name> [-t <type>] [--hash <hash>]\n";
    echo "  ./register.php -u --hash <hash> [-k <key>] [-t <type>]\n\n";
    echo "Options:\n";
    echo "  -n, --name     Specify the name for the registered station or client (required for new registrations).\n";
    echo "  -t, --type     Specify registration type: 'station', 'client' (default: 'station').\n";
    echo "  --hash         Specify a pre-existing hash (optional for new, required for update).\n";
    echo "  -u, --update   Enable update mode to change the key for an existing hash.\n";
    echo "  -k, --key      Specify a custom key value (optional; generates a secure random key if omitted).\n";
    echo "  -h, --help     Show this help message.\n\n";
    echo "Examples:\n";
    echo "  ./register.php --type client --name \"ThinkPad-X1\"\n";
    echo "  ./register.php --update --hash \"uuid-hash\" --key \"custom-api-key\"\n\n";
    exit(0);
}

// 2. Load configurations gracefully
$lib_path = dirname(__DIR__) . "/piwem/lib/";
$config_file = $lib_path . "config.php";

if (!file_exists($config_file)) {
    $config_file = $lib_path . "config.php.sample";
}

if (!file_exists($config_file)) {
    fwrite(STDERR, "Error: Configuration file (config.php or config.php.sample) not found at: " . $lib_path . "\n");
    exit(1);
}

if (!file_exists($lib_path . "SQL.php")) {
    fwrite(STDERR, "Error: SQL library (SQL.php) not found at: " . $lib_path . "\n");
    exit(1);
}

require $lib_path . "SQL.php";
require $config_file;

// 3. Helper functions
function uuidv4() {
    $data = openssl_random_pseudo_bytes(16);
    $data[6] = chr(ord($data[6]) & 0x0f | 0x40); // set version to 0100
    $data[8] = chr(ord($data[8]) & 0x3f | 0x80); // set bits 6-7 to 10
    return vsprintf('%s%s-%s-%s-%s-%s%s%s', str_split(bin2hex($data), 4));
}

function generate_key() {
    return bin2hex(openssl_random_pseudo_bytes(16));
}

// 4. Validate registration inputs
$is_update = isset($options['u']) || isset($options['update']);

$custom_key = null;
if (isset($options['key'])) {
    $custom_key = $options['key'];
} elseif (isset($options['k'])) {
    $custom_key = $options['k'];
}

$entry_hash = isset($options['hash']) ? $options['hash'] : null;

if ($is_update) {
    if (!$entry_hash) {
        fwrite(STDERR, "Error: --hash is required when updating.\n");
        exit(1);
    }
} else {
    if (!isset($options['name']) && !isset($options['n'])) {
        fwrite(STDERR, "Error: --name (-n) is required.\nUse -h or --help for instructions.\n");
        exit(1);
    }
}

$name = (isset($options['name']) ? $options['name'] : (isset($options['n']) ? $options['n'] : null));

$type = "station";
if (isset($options['type'])) {
    $type = $options['type'];
} elseif (isset($options['t'])) {
    $type = $options['t'];
}

$type = strtolower($type);
if ($type === "client") {
    $type = "client";
}

if ($type !== "station" && $type !== "client") {
    fwrite(STDERR, "Error: --type (-t) must be 'station' or 'client'.\n");
    exit(1);
}

// 5. Connect and insert/update
$sql = new SQL($WWWconfig['SQL']);

if ($is_update) {
    // Verify that hash exists
    $prep = $sql->conn->prepare("SELECT station_name FROM `" . $sql->db . "`.`Stations` WHERE station_hash = ?");
    $prep->execute(array($entry_hash));
    $result = $prep->fetch(PDO::FETCH_ASSOC);

    if (!$result) {
        fwrite(STDERR, "Error: Hash '" . $entry_hash . "' is not registered. Cannot update.\n");
        exit(1);
    }

    $name = $name ? $name : $result['station_name'];
    $entry_key = $custom_key ? $custom_key : generate_key();

    // Perform key and type update
    $prep = $sql->conn->prepare("UPDATE `" . $sql->db . "`.`Stations` SET station_key = ?, `type` = ? WHERE station_hash = ?");
    $prep->execute(array($entry_key, $type, $entry_hash));

    $console_string = " key and type updated ";
}else
{
    // Normal Registration mode
    if ($entry_hash) {
        // Check if hash already exists
        $prep = $sql->conn->prepare("SELECT station_key FROM `" . $sql->db . "`.`Stations` WHERE station_hash = ?");
        $prep->execute(array($entry_hash));
        $result = $prep->fetch(PDO::FETCH_ASSOC);

        if ($result) {
            echo "===================================================================\n";
            echo " WARNING: This hash is already registered in the database!\n";
            echo " To update its key, run the script with the -u / --update switch.\n";
            echo "===================================================================\n\n";
            exit(0);
        }
    } else {
        $entry_hash = uuidv4();
        echo "No hash provided. Generated new UUID: " . $entry_hash . "\n";
    }

    $entry_key = generate_key();
    $timestamp = date("Y-m-d H:i:s");

    // Insert new row
    $prep = $sql->conn->prepare("INSERT INTO `" . $sql->db . "`.`Stations` (station_key, station_hash, station_name, `timestamp`, `type`) VALUES (?, ?, ?, ?, ?)");
    $prep->execute(array($entry_key, $entry_hash, $name, $timestamp, $type));
    $console_string = " registered ";
}


echo "\n===================================================================\n";
echo " SUCCESS: " . ucfirst($type) . $console_string."successfully!\n";
echo "===================================================================\n";
echo " Name: " . $name . "\n";
echo " Hash: " . $entry_hash . "\n";
echo " Key:  " . $entry_key . "\n";
echo "===================================================================\n";
echo " Next Steps:\n";
if ($type === "client") {
    echo " Please open your DesktopClient's 'settings.ini' file and add:\n";
    echo "     Desktop Client Hash = " . $entry_hash . "\n";
    echo "     Desktop Client Key = " . $entry_key . "\n";
} else {
    echo " Please configure your WeatherStation's 'settings.ini' file:\n";
    echo "     station_hash = " . $entry_hash . "\n";
    echo "     station_key = " . $entry_key . "\n";
}
echo "===================================================================\n\n";