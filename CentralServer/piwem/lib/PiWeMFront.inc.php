<?php
/*
index.php
Copyright (C) 2016 Phil Ferland

This program is free software; you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation; either
version 2 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

ou should have received a copy of the GNU General Public License along with this program;
if not, write to the

   Free Software Foundation, Inc.,
   59 Temple Place, Suite 330,
   Boston, MA 02111-1307 USA
*/
class PiWeMFront
{
    function __construct($WWWconfig = array())
    {
        if( @$WWWconfig === array() )
        {
            throw new Exception('$WWWconfig is not set!');
        }
        require "lib/SQL.php"; #the uh.. SQL class...
        require_once '/usr/share/php/Twig/autoload.php';
        #now lets build the SQL class.
        $this->Alt_Sensor = $WWWconfig['http']['Alt_Sensor'];
        $this->debug = 0;
        $this->SQL = new SQL($WWWconfig['SQL']);
        
        if (session_status() === PHP_SESSION_NONE) {
            session_start();
        }

        // Resolve active theme: REQUEST parameter > Session > Cookie > config.php default
        if (isset($_REQUEST['theme'])) {
            $theme = $_REQUEST['theme'];
            $_SESSION['piwem_theme'] = $theme;
            setcookie('piwem_theme', $theme, time() + (86400 * 30), "/"); // 30 days
            $_COOKIE['piwem_theme'] = $theme; // Populate for the current request context too
        } elseif (isset($_SESSION['piwem_theme'])) {
            $theme = $_SESSION['piwem_theme'];
        } elseif (isset($_COOKIE['piwem_theme'])) {
            $theme = $_COOKIE['piwem_theme'];
        } else {
            $theme = isset($WWWconfig['http']['theme']) ? $WWWconfig['http']['theme'] : 'default';
        }
        
        // Sanitize theme string to prevent directory traversal
        $theme = preg_replace('/[^a-zA-Z0-9_\-]/', '', $theme);
        if (empty($theme)) {
            $theme = 'default';
        }

        $loader = new \Twig\Loader\FilesystemLoader();
        
        $theme_dir = dirname(__DIR__) . '/templates/themes/' . $theme;
        if ($theme !== 'default' && is_dir($theme_dir)) {
            $loader->addPath($theme_dir);
        }
        $loader->addPath(dirname(__DIR__) . '/templates/default');
        
        $this->twig = new \Twig\Environment($loader, [
            'cache' => false,
            'debug' => true,
        ]);

        $this->twig->addGlobal('current_theme', $theme);
        $this->twig->addGlobal('available_themes', $this->GetAvailableThemes());
    }

    function GetStations()
    {
        try {
            $result = $this->SQL->conn->query("SELECT `station_name`, `station_hash`, `lastupdate` FROM `" . $this->SQL->db . "`.`Stations` WHERE `type` = 'station' ORDER BY id ASC");
        } catch (PDOException $e) {
            // Fallback if the 'type' column does not exist on some database instances
            $result = $this->SQL->conn->query("SELECT `station_name`, `station_hash`, `lastupdate` FROM `" . $this->SQL->db . "`.`Stations` ORDER BY id ASC");
        }
        $fetch = $result->fetchAll(2);
        return $fetch;
    }

    function GetStationInfo($station_hash)
    {
        $prep = $this->SQL->conn->prepare("SELECT `station_name`, `station_hash`, `lastupdate` FROM `" . $this->SQL->db . "`.`Stations` WHERE `station_hash` = ? ORDER BY id ASC");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $fetch = $prep->fetch(2);
        return $fetch;
    }

    function GetStationAltitude($station_hash = "", $sensor = "")
    {
        $query_table = (!empty($sensor)) ? $sensor : "bmp280";
        $prep = $this->SQL->conn->prepare("SELECT altitude FROM `" . $this->SQL->db . "`.`$query_table` WHERE `station_hash` = ? AND `altitude` != 0 ORDER BY `id` DESC LIMIT 1");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $row = $prep->fetch(2);
        if ($row) {
            return $row['altitude'];
        }
        
        // Fallback if no non-zero altitude is found
        $prep = $this->SQL->conn->prepare("SELECT altitude FROM `" . $this->SQL->db . "`.`$query_table` WHERE `station_hash` = ? ORDER BY `id` DESC LIMIT 1");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $row = $prep->fetch(2);
        return isset($row['altitude']) ? $row['altitude'] : 0.0;
    }

    function GetStationSensorData($station_hash = "", $sensor = "", $limit = 1)
    {
        $cols = array();
        $not_zero_field = "";

        switch ($sensor) {
            case 'dht11':
                $cols = array('c_temp', 'f_temp', 'humidity', 'timestamp');
                $not_zero_field = "humidity";
                break;
            case 'dht22':
                $cols = array('c_temp', 'f_temp', 'humidity', 'timestamp');
                $not_zero_field = "humidity";
                break;
            case 'am2302':
                $cols = array('c_temp', 'f_temp', 'humidity', 'timestamp');
                $not_zero_field = "humidity";
                break;
            case 'am3202':
                $cols = array('c_temp', 'f_temp', 'humidity', 'timestamp');
                $not_zero_field = "humidity";
                break;
            case 'bmp085':
                $cols = array('c_temp', 'f_temp', 'pressure', 'altitude', 'timestamp');
                $not_zero_field = "pressure";
                break;
            case 'bmp180':
                $cols = array('c_temp', 'f_temp', 'pressure', 'altitude', 'timestamp');
                $not_zero_field = "pressure";
                break;
            case 'bmp280':
                $cols = array('c_temp', 'f_temp', 'pressure', 'altitude', 'timestamp');
                $not_zero_field = "pressure";
                break;
            case 'analog_temp_sensor':
                $cols = array('c_temp', 'f_temp', 'timestamp');
                $not_zero_field = "c_temp";
                break;
            case 'thermistor':
                $cols = array('c_temp', 'f_temp', 'timestamp');
                $not_zero_field = "c_temp";
                break;
            case 'db18s20':
                $cols = array('c_temp', 'f_temp', 'timestamp');
                $not_zero_field = "c_temp";
                break;
            case 'photoresistor':
                $cols = array('photolevel', 'timestamp');
                $not_zero_field = "photolevel";
                break;
            case 'wind_speed':
                $cols = array('wind_mps', 'timestamp');
                $not_zero_field = "wind_mps";
                break;
            case 'wind_direction':
                $cols = array('wind_direction', 'timestamp');
                $not_zero_field = "wind_direction";
                break;
            default:
                $cols = array('c_temp', 'f_temp', 'humidity', 'pressure', 'altitude', 'photolevel', 'timestamp');
                break;
        }

        $query = "SELECT " . implode(", ", $cols) . " FROM `" . $this->SQL->db . "`.`$sensor` WHERE `station_hash` = ?";
        if ($not_zero_field !== "") {
            $query .= " AND `$not_zero_field` != 0";
        }
        
        $is_time_interval = false;
        if (is_string($limit) && preg_match('/^(\d+\s+)(MINUTE|HOUR|DAY|WEEK|MONTH)S?$/i', trim($limit), $matches)) {
            $is_time_interval = true;
            $interval = $matches[1] . $matches[2]; // Convert to singular for SQL compatibility
            $query .= " AND `timestamp` >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL $interval)";
        }

        $query .= " ORDER BY `timestamp` DESC";
        
        if (!$is_time_interval && $limit !== 'all' && (int)$limit !== 0) {
            $query .= " LIMIT " . (int)$limit;
        }

        if ($this->debug) {
            var_dump($query);
        }

        $prep = $this->SQL->conn->prepare($query);
        if ($prep === false) {
            return 0;
        }
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $res = $prep->execute();
        if ($res === false) {
            return 0;
        }

        if ($limit === 1) {
            $fetch = $prep->fetch(2);
        } else {
            $fetch = $prep->fetchAll(2);
        }
        return $fetch;
    }

    function GetStationSensors($station_hash = "")
    {
        $prep = $this->SQL->conn->prepare("SELECT dht11, dht22, bmp085, bmp180, bmp280, thermistor, analog_temp_sensor, photoresistor, camera, am2302 FROM `" . $this->SQL->db . "`.`Station_sensors` WHERE station_hash = ? LIMIT 1");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $row = $prep->fetch(2);
        
        if ($row) {
            return $row;
        }

        // Fallback: probe each table to see if any data has been uploaded for this station
        $sensors = array(
            'dht11' => 0,
            'dht22' => 0,
            'bmp085' => 0,
            'bmp180' => 0,
            'bmp280' => 0,
            'thermistor' => 0,
            'analog_temp_sensor' => 0,
            'photoresistor' => 0,
            'camera' => 0,
            'am2302' => 0
        );

        $has_data = false;
        foreach ($sensors as $sensor => &$val) {
            try {
                $check = $this->SQL->conn->prepare("SELECT 1 FROM `" . $this->SQL->db . "`.`$sensor` WHERE station_hash = ? LIMIT 1");
                $check->bindParam(1, $station_hash, PDO::PARAM_STR);
                $check->execute();
                if ($check->fetch()) {
                    $val = 1;
                    $has_data = true;
                }
            } catch (PDOException $e) {
                // Table might not exist, ignore
            }
        }

        return $has_data ? $sensors : false;
    }

    function GetAvailableThemes()
    {
        $themes = array('default');
        $themes_dir = dirname(__DIR__) . '/templates/themes';
        if (is_dir($themes_dir)) {
            $dirs = scandir($themes_dir);
            foreach ($dirs as $dir) {
                if ($dir !== '.' && $dir !== '..' && is_dir($themes_dir . '/' . $dir)) {
                    $themes[] = $dir;
                }
            }
        }
        return $themes;
    }
}
?>
