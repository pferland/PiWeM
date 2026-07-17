<?php

require "../lib/SQL.php"; #the uh.. SQL class...


class PiWeMAPI
{
    function __construct($WWWconfig)
    {
        if( @$WWWconfig['SQL'] == "" )
        {
            throw new Exception('$WWWconfig[\'SQL\'] is not set!');
        }
        $this->debug = 0;
        #now lets build the SQL class.
        $this->SQL = new SQL($WWWconfig['SQL']);

        $this->payload      = "";
        $this->station_name = "";
        $this->station_hash = "";
        $this->station_key  = "";
        $this->timestamp    = "";
    }

    function checkapikey()
    {
        if(!$this->station_hash)
        {
            throw new Exception("Station Hash not set.");
        }
        if(!$this->station_key)
        {
            throw new Exception("Station Key not set.");
        }

        $prep = $this->SQL->conn->prepare("SELECT station_name FROM `".$this->SQL->db."`.`Stations` WHERE station_hash = ? AND station_key = ?");
        $prep->bindParam(1, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_key, PDO::PARAM_STR);
        $prep->execute();
        $result = $prep->fetch(2);
        if(!@$result['station_name'])
        {
            return 0;
        }else
        {
            return 1;
        }
    }


    ##########################
    ##########################
    ##########################
    # Import data API Methods
    ##########################
    ##########################
    ##########################


    function importdata()
    {
        if(!isset($this->payload) || empty($this->payload))
        {
            throw new Exception("Payload is not set or empty.");
        }

        $json_data = json_decode($this->payload, True);
        if (!$json_data) {
            throw new Exception("Invalid JSON payload.");
        }

        $station_name = "";
        $station_hash = $this->station_hash;
        $timestamp = $this->timestamp;

        if (isset($json_data['station_name'])) {
            $station_name = $json_data['station_name'];
        }
        if (isset($json_data['station_hash'])) {
            $station_hash = $json_data['station_hash'];
        }
        if (isset($json_data['timestamp'])) {
            $timestamp = $json_data['timestamp'];
        }

        // Initialize all schema fields to default values
        $pressure = 0.0;
        $altitude = 0.0;
        $photolevel = 0;
        $c_temp = 0;
        $f_temp = 0;
        $humidity = 0;
        $voltage = 0.0;
        $shunt_mV = 0.0;
        $current_mA = 0;
        $power_mW = 0.0;
        $power_channel = 0;
        $wind_mps = 0.0;
        $wind_direction = 0;

        if (isset($json_data['station_data']) && is_array($json_data['station_data'])) {
            $data = $json_data['station_data'];

            // 1. Temperature & Humidity & Pressure & Altitude from BMP sensors
            foreach (['bmp280', 'bmp180', 'bmp085'] as $bmp) {
                if (isset($data[$bmp]) && is_array($data[$bmp])) {
                    $b = $data[$bmp];
                    if (isset($b['pressure'])) {
                        $pressure = (float)$b['pressure'];
                    }
                    if (isset($b['altitude'])) {
                        $altitude = (float)$b['altitude'];
                    }
                    if (isset($b['temp']) && is_array($b['temp'])) {
                        $c_temp = (int)$b['temp'][0];
                        $f_temp = (int)$b['temp'][1];
                    } elseif (isset($b['temperature'])) {
                        $c_temp = (int)$b['temperature'];
                        $f_temp = (int)($c_temp * 1.8 + 32);
                    }
                    break; // Use the first available BMP sensor
                }
            }

            // 2. Humidity & Temperature from DHT / AM2302 sensors
            foreach (['dht22', 'am2302', 'dht11'] as $dht) {
                if (isset($data[$dht]) && is_array($data[$dht])) {
                    $d = $data[$dht];
                    if (isset($d['humidity'])) {
                        $humidity = (int)$d['humidity'];
                    }
                    // Only overwrite temperature if not already set by BMP
                    if ($c_temp == 0) {
                        if (isset($d['temp']) && is_array($d['temp'])) {
                            $c_temp = (int)$d['temp'][0];
                            $f_temp = (int)$d['temp'][1];
                        } elseif (isset($d['temperature'])) {
                            $c_temp = (int)$d['temperature'];
                            $f_temp = (int)($c_temp * 1.8 + 32);
                        }
                    }
                    break; // Use first available DHT/AM2302 sensor
                }
            }

            // 3. Temperature from ats or therm (analog temperature / thermistor)
            if ($c_temp == 0) {
                if (isset($data['ats']) && is_array($data['ats'])) {
                    $c_temp = (int)$data['ats'][0];
                    $f_temp = (int)$data['ats'][1];
                } elseif (isset($data['therm']) && is_array($data['therm'])) {
                    $c_temp = (int)$data['therm'][0];
                    $f_temp = (int)$data['therm'][1];
                }
            }

            // 4. Photoresistor
            if (isset($data['photoresistor'])) {
                $photolevel = (int)$data['photoresistor'];
            }

            // 6. Wind monitoring
            if (isset($data['wind']) && is_array($data['wind'])) {
                $w = $data['wind'];
                $wind_mps = isset($w['wind_mps']) ? (float)$w['wind_mps'] : (isset($w['meters_per_second']) ? (float)$w['meters_per_second'] : 0.0);
                $wind_direction = isset($w['wind_direction']) ? (int)$w['wind_direction'] : (isset($w['direction']) ? (int)$w['direction'] : 0);
            }
        }

        // Insert consolidated sensor row
        $prep = $this->SQL->conn->prepare("INSERT INTO `".$this->SQL->db."`.`weather_data` 
            (pressure, altitude, photolevel, c_temp, f_temp, humidity, wind_mps, wind_direction, timestamp, station_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");

        $prep->bindParam(1, $pressure);
        $prep->bindParam(2, $altitude);
        $prep->bindParam(3, $photolevel, PDO::PARAM_INT);
        $prep->bindParam(4, $c_temp, PDO::PARAM_INT);
        $prep->bindParam(5, $f_temp, PDO::PARAM_INT);
        $prep->bindParam(6, $humidity, PDO::PARAM_INT);
        $prep->bindParam(7, $wind_mps);
        $prep->bindParam(8, $wind_direction, PDO::PARAM_INT);
        $prep->bindParam(9, $timestamp, PDO::PARAM_STR);
        $prep->bindParam(10, $station_hash, PDO::PARAM_STR);

        $prep->execute();

        // Update lastupdate timestamp on Stations
        $this->timestamp = $timestamp;
        $this->station_hash = $station_hash;
        $this->UpdateStationTimestamp();

        print "1";
    }

    function UpdateStationTimestamp()
    {
        if($this->timestamp === "")
        {return 0;}
        $prep = $this->SQL->conn->prepare("UPDATE `".$this->SQL->db."`.`Stations` SET `lastupdate` = ? WHERE station_hash = ?");
        $prep->bindParam(1, $this->timestamp, PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_hash, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }


    ##########################
    ##########################
    ##########################
    # Read data API Methods
    ##########################
    ##########################
    ##########################

    function read_data()
    {
        $limit = isset($_REQUEST['limit']) ? $_REQUEST['limit'] : 100;
        $query_hash = isset($_REQUEST['target_hash']) ? $_REQUEST['target_hash'] : $this->station_hash;

        // Get active sensors for this station
        $sensors = $this->GetStationSensors($query_hash);
        if (!$sensors) {
            header('Content-Type: application/json');
            echo json_encode(array());
            return;
        }

        $all_rows = array();

        foreach ($sensors as $sensor => $active) {
            if (!$active) continue;
            
            // Map wind_mps column to wind_speed table
            $sensor_table = $sensor;
            if ($sensor === 'wind_mps') {
                $sensor_table = 'wind_speed';
            }
            if ($sensor === 'wind_direction') {
                $sensor_table = 'wind_direction';
            }

            // Determine columns to select
            $cols = array('timestamp');
            switch ($sensor) {
                case 'dht11':
                case 'dht22':
                case 'am2302':
                    $cols[] = 'c_temp';
                    $cols[] = 'f_temp';
                    $cols[] = 'humidity';
                    break;
                case 'bmp085':
                case 'bmp180':
                case 'bmp280':
                    $cols[] = 'c_temp';
                    $cols[] = 'f_temp';
                    $cols[] = 'pressure';
                    $cols[] = 'altitude';
                    break;
                case 'analog_temp_sensor':
                case 'thermistor':
                    $cols[] = 'c_temp';
                    $cols[] = 'f_temp';
                    break;
                case 'photoresistor':
                    $cols[] = 'photolevel';
                    break;
                case 'wind_mps':
                    $cols[] = 'wind_mps';
                    break;
                case 'wind_direction':
                    $cols[] = 'wind_direction';
                    break;
            }

            $query = "SELECT " . implode(", ", $cols) . " FROM `" . $this->SQL->db . "`.`$sensor_table` WHERE station_hash = ?";
            
            $is_time_interval = false;
            if (is_string($limit) && preg_match('/^(\d+\s+)(MINUTE|HOUR|DAY|WEEK|MONTH)S?$/i', trim($limit), $matches)) {
                $is_time_interval = true;
                $interval = $matches[1] . $matches[2];
                $query .= " AND `timestamp` >= DATE_SUB(UTC_TIMESTAMP(), INTERVAL $interval)";
            }
            
            $query .= " ORDER BY `timestamp` DESC";
            
            if (!$is_time_interval) {
                $int_limit = (int)$limit;
                if ($int_limit <= 0) $int_limit = 1;
                if ($int_limit > 500) $int_limit = 500;
                $query .= " LIMIT " . $int_limit;
            }

            try {
                $prep = $this->SQL->conn->prepare($query);
                $prep->bindParam(1, $query_hash, PDO::PARAM_STR);
                $prep->execute();
                $rows = $prep->fetchAll(2);
                foreach ($rows as $row) {
                    $all_rows[] = $row;
                }
            } catch (PDOException $e) {
                // Table might not exist or empty, ignore
            }
        }

        // Sort all rows by timestamp DESC
        usort($all_rows, function($a, $b) {
            return strcmp($b['timestamp'], $a['timestamp']); // DESC order
        });

        // Group rows in a single linear pass
        $combined = array();
        $current_group = null;
        $current_time = 0;

        foreach ($all_rows as $row) {
            $ts = $row['timestamp'];
            $ts_time = strtotime($ts);

            if ($current_group === null || abs($current_time - $ts_time) > 5) {
                if ($current_group !== null) {
                    $combined[] = $current_group;
                }
                $current_group = array('timestamp' => $ts);
                $current_time = $ts_time;
            }

            foreach ($row as $k => $v) {
                if ($k !== 'timestamp') {
                    $current_group[$k] = $v;
                }
            }
        }
        if ($current_group !== null) {
            $combined[] = $current_group;
        }

        // Slice to limit if it is a number
        $result = $combined;
        if (is_numeric($limit)) {
            $result = array_slice($result, 0, (int)$limit);
        }

        header('Content-Type: application/json');
        echo json_encode($result);
    }

    function GetStationSensors($station_hash = "")
    {
        try {
            $prep = $this->SQL->conn->prepare("SELECT dht11, dht22, bmp085, bmp180, bmp280, thermistor, analog_temp_sensor, photoresistor, am2302 FROM `" . $this->SQL->db . "`.`Station_sensors` WHERE station_hash = ? LIMIT 1");
            $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
            $prep->execute();
            $row = $prep->fetch(2);
            if ($row) {
                return $row;
            }
        } catch (PDOException $e) {
            // Ignore, proceed to fallback
        }

        // Fallback: probe each table
        $sensors = array(
            'dht11' => 0,
            'dht22' => 0,
            'bmp085' => 0,
            'bmp180' => 0,
            'bmp280' => 0,
            'thermistor' => 0,
            'analog_temp_sensor' => 0,
            'photoresistor' => 0,
            'am2302' => 0,
            'wind_mps' => 0,
            'wind_direction' => 0
        );

        $has_data = false;
        foreach ($sensors as $sensor => &$val) {
            $table = $sensor;
            if ($sensor === 'wind_mps') $table = 'wind_speed';
            if ($sensor === 'wind_direction') $table = 'wind_direction';
            try {
                $check = $this->SQL->conn->prepare("SELECT 1 FROM `" . $this->SQL->db . "`.`$table` WHERE station_hash = ? LIMIT 1");
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

    function list_stations()
    {
        try {
            $prep = $this->SQL->conn->prepare("SELECT `station_name`, `station_hash`, `lastupdate` FROM `".$this->SQL->db."`.`Stations` WHERE `type` = 'station' ORDER BY `id` ASC");
        } catch (PDOException $e) {
            $prep = $this->SQL->conn->prepare("SELECT `station_name`, `station_hash`, `lastupdate` FROM `".$this->SQL->db."`.`Stations` ORDER BY `id` ASC");
        }
        $prep->execute();
        $fetch = $prep->fetchAll(2);
        header('Content-Type: application/json');
        echo json_encode($fetch);
    }
}
