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

        $prep = $this->SQL->conn->prepare("SELECT station_name FROM `weather_data`.`Stations` WHERE station_hash = ? AND station_key = ?");
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


    function importdata()
    {
        if(!isset($this->payload) || empty($this->payload))
        {
            throw new Exception("Payload is not set or empty.");
        }

        $json_data = json_decode($this->payload, True);

        foreach($json_data as $key=>$value)
        {
            #var_dump($key, $value);
            switch($key)
            {
                case "station_name":
                    $this->station_name = $value;
                    break;
                case "timestamp":
                    $this->timestamp = $value;
                    break;
                case "station_hash":
                    $this->station_hash = $value;
                    break;
                case "station_data":
                    foreach($value as $subkey=>$sensor)
                    {
                        var_dump($subkey, $sensor);
                        switch($subkey)
                        {
                            case "bmp085":
                                print $this->import_BMP085($value);
                                break;
                            case "bmp180":
                                print $this->import_BMP180($value);
                                break;
                            case "bmp280":
                                print $this->import_BMP280($value);
                                break;
                            case "dht11":
                                print $this->import_DHT11($value);
                                break;
                            case "dht22":
                                print $this->import_DHT22($value);
                                break;
                            case "am2302":
                                print $this->import_AM2302($value);
                                break;
                            case "ats":
                                print $this->import_ATS($value);
                                break;
                            case "photoresistor":
                                print $this->import_photoresistor($value);
                                break;
                            case "therm":
                                print $this->import_thermistor($value);
                                break;
                        }
                        print "------------------------------------<br>\r\n";
                    }
                    break;
            }
        }
        $this->UpdateStationTimestamp();
    }

    function UpdateStationTimestamp()
    {
        if($this->timestamp === "")
        {return 0;}
        $prep = $this->SQL->conn->prepare("UPDATE `weather_data`.`Stations` SET `lastupdate` = ? WHERE station_hash = ?");
        $prep->bindParam(1, $this->timestamp, PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_hash, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_BMP085($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`bmp085` (pressure, c_temp, f_temp, altitude, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['pressure'], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(3, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(4, $data['altitude'], PDO::PARAM_STR);
        $prep->bindParam(5, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(6, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_BMP180($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`bmp180` (pressure, c_temp, f_temp, altitude, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['pressure'], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(3, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(4, $data['altitude'], PDO::PARAM_STR);
        $prep->bindParam(5, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(6, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_BMP280($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`bmp280` (pressure, c_temp, f_temp, altitude, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['pressure'], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(3, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(4, $data['altitude'], PDO::PARAM_STR);
        $prep->bindParam(5, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(6, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_DHT11($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`dht11` (c_temp, f_temp, humidity, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(3, $data['humidity'], PDO::PARAM_STR);
        $prep->bindParam(4, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(5, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_DHT22($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`dht22` (c_temp, f_temp, humidity, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(3, $data['humidity'], PDO::PARAM_STR);
        $prep->bindParam(4, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(5, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_AM2302($data)
    {
        if(empty($data))
        {return 0;}

        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`am2302` (c_temp, f_temp, humidity, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(3, $data['humidity'], PDO::PARAM_STR);
        $prep->bindParam(4, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(5, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_ATS($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`analog_temp_sensor` (c_temp, f_temp, station_hash, `timestamp`) VALUES (?, ?, ?, ?)");
        $prep->bindParam(1, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(3, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(4, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_thermistor($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`thermistor` (c_temp, f_temp, station_hash, `timestamp`) VALUES (?, ?, ?, ?)");
        $prep->bindParam(1, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(4, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(5, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function import_photoresistor($data)
    {
        if(empty($data))
        {return 0;}
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`photoresistor` (photolevel, station_hash, `timestamp`) VALUES (?, ?, ?)");
        $prep->bindParam(1, $data['photoresistor'], PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(3, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

    function insert_station()
    {
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`Stations` ( station_name, station_hash, station_key, `timestamp`) VALUES (?, ?, ?, ?)");
        $prep->bindParam(1, $this->station_name, PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(4, $this->station_key, PDO::PARAM_STR);
        $prep->bindParam(5, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        return 1;
    }

}