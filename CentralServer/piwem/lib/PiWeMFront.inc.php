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
        require $WWWconfig['http']['smarty_path']."Smarty.class.php"; #get smarty..
        #now lets build the SQL class.
        $this->Alt_Sensor = $WWWconfig['http']['Alt_Sensor'];
        $this->debug = 0;
        $this->SQL = new SQL($WWWconfig['SQL']);
        $this->smarty = new smarty();
    }

    function GetStations()
    {
        $result = $this->SQL->conn->query("SELECT `station_name`, `station_hash`, `lastupdate` FROM `" . $this->SQL->db . "`.`Stations` ORDER BY id ASC");
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
        $prep = $this->SQL->conn->prepare("SELECT altitude FROM `" . $this->SQL->db . "`.`weather_data` WHERE `station_hash` = ? AND `altitude` != 0 ORDER BY `id` DESC LIMIT 1");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $row = $prep->fetch(2);
        if ($row) {
            return $row['altitude'];
        }
        
        // Fallback if no non-zero altitude is found
        $prep = $this->SQL->conn->prepare("SELECT altitude FROM `" . $this->SQL->db . "`.`weather_data` WHERE `station_hash` = ? ORDER BY `id` DESC LIMIT 1");
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
            case 'dht22':
            case 'am2302':
            case 'am3202':
                $cols = array('c_temp', 'f_temp', 'humidity', 'timestamp');
                $not_zero_field = "humidity";
                break;
            case 'bmp085':
            case 'bmp180':
            case 'bmp280':
                $cols = array('c_temp', 'f_temp', 'pressure', 'altitude', 'timestamp');
                $not_zero_field = "pressure";
                break;
            case 'analog_temp_sensor':
            case 'thermistor':
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

        $query = "SELECT " . implode(", ", $cols) . " FROM `" . $this->SQL->db . "`.`weather_data` WHERE `station_hash` = ?";
        if ($not_zero_field !== "") {
            $query .= " AND `$not_zero_field` != 0";
        }
        $query .= " ORDER BY `timestamp` DESC";
        if ($limit !== 0) {
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
        $fetch = $prep->fetch(2);
        if ($this->debug) {
            var_dump($fetch);
        }
        return $fetch;
    }

    function GetStationPower($station_hash = "", $limit = 500, $order = "DESC")
    {
        $order = (strtoupper($order) === "ASC") ? "ASC" : "DESC";
        $ret = array();
        
        $prep = $this->SQL->conn->prepare("SELECT `shunt_mV`, `voltage`, `timestamp` FROM `" . $this->SQL->db . "`.`weather_data` WHERE station_hash = ? AND (`voltage` != 0 OR `shunt_mV` != 0) ORDER BY id $order LIMIT " . (int)$limit);
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $ret['voltage'] = $prep->fetchAll(2);
        if ($this->debug) {
            var_dump($ret['voltage']);
        }
        
        $prep = $this->SQL->conn->prepare("SELECT `current_mA`, `timestamp` FROM `" . $this->SQL->db . "`.`weather_data` WHERE station_hash = ? AND (`voltage` != 0 OR `shunt_mV` != 0) ORDER BY id $order LIMIT " . (int)$limit);
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $ret['current'] = $prep->fetchAll(2);
        if ($this->debug) {
            var_dump($ret['current']);
        }
        
        $prep = $this->SQL->conn->prepare("SELECT `power_mW`, `timestamp` FROM `" . $this->SQL->db . "`.`weather_data` WHERE station_hash = ? AND (`voltage` != 0 OR `shunt_mV` != 0) ORDER BY id $order LIMIT " . (int)$limit);
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $ret['power'] = $prep->fetchAll(2);
        if ($this->debug) {
            var_dump($ret['power']);
        }
        return $ret;
    }

}