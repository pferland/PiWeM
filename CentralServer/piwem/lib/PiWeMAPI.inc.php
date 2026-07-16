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
        $limit = isset($_REQUEST['limit']) ? (int)$_REQUEST['limit'] : 1;

        if ($limit <= 0) $limit = 1;
        if ($limit > 100) $limit = 100;

        $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM `".$this->SQL->db."`.`weather_data` WHERE station_hash = ? ORDER BY `id` DESC LIMIT " . $limit);
        $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
        $prep->execute();
        $fetch = $prep->fetchAll(2);
        var_dump($fetch);
    }
}
