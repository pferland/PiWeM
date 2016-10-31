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
                        #var_dump($subkey, $sensor);
                        switch($subkey)
                        {
                            case "bmp085":
                                print $this->import_BMP085($sensor);
                                break;
                            case "bmp180":
                                print $this->import_BMP180($sensor);
                                break;
                            case "bmp280":
                                print $this->import_BMP280($sensor);
                                break;
                            case "dht11":
                                print $this->import_DHT11($sensor);
                                break;
                            case "dht22":
                                print $this->import_DHT22($sensor);
                                break;
                            case "am2302":
                                print $this->import_AM2302($sensor);
                                break;
                            case "ats":
                                print $this->import_ATS($sensor);
                                break;
                            case "photoresistor":
                                print $this->import_photoresistor($sensor);
                                break;
                            case "therm":
                                print $this->import_thermistor($sensor);
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
        var_dump("------------------------------------------------\r\n------------------------\r\n--------------------------------------------");
        var_dump($data);
        $prep = $this->SQL->conn->prepare("INSERT INTO `weather_data`.`bmp280` (pressure, c_temp, f_temp, altitude, station_hash, `timestamp`) VALUES (?, ?, ?, ?, ?, ?)");
        $prep->bindParam(1, $data['pressure'], PDO::PARAM_STR);
        $prep->bindParam(2, $data['temp'][0], PDO::PARAM_STR);
        $prep->bindParam(3, $data['temp'][1], PDO::PARAM_STR);
        $prep->bindParam(4, $data['altitude'], PDO::PARAM_STR);
        $prep->bindParam(5, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(6, $this->timestamp, PDO::PARAM_STR);
        $prep->execute();
        var_dump("------------------------------------------------\r\n------------------------\r\n--------------------------------------------");
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
        $prep->bindParam(1, $data[0], PDO::PARAM_STR);
        $prep->bindParam(2, $data[1], PDO::PARAM_STR);
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
        $prep->bindParam(1, $data, PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(3, $this->timestamp, PDO::PARAM_STR);
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
        switch(strtolower($_REQUEST['sensor']))
        {
            case "dht11":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM weather_data.dht11 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM weather_data.dht11 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "dht22":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM weather_data.dht22 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM weather_data.dht22 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "bmp085":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `pressure`, `c_temp`, `f_temp` FROM weather_data.bmp085 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `pressure`, `c_temp`, `f_temp` FROM weather_data.bmp085 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "bmp180":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `pressure`, `c_temp`, `f_temp` FROM weather_data.bmp180 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `pressure`, `c_temp`, `f_temp` FROM weather_data.bmp180 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "bmp280":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `pressure`, `c_temp`, `f_temp` FROM weather_data.bmp280 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `pressure`, `c_temp`, `f_temp` FROM weather_data.bmp280 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "am2302":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM weather_data.am2302 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `humidity`, `c_temp`, `f_temp` FROM weather_data.am2302 WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "photoresistor":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `photolevel` FROM weather_data.photoresistor WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `photolevel` FROM weather_data.photoresistor WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "ats":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `c_temp`, `f_temp` FROM weather_data.analog_temp_sensor WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `c_temp`, `f_temp` FROM weather_data.analog_temp_sensor WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "thermistor":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `c_temp`, `f_temp` FROM weather_data.thermistor WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `c_temp`, `f_temp` FROM weather_data.thermistor WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;

            case "camera":
                if(@$_REQUEST['limit'])
                {
                    $prep = $this->SQL->conn->prepare("SELECT `file` FROM weather_data.camera WHERE station_hash = ? ORDER BY `id` DESC LIMIT 100");
                }else
                {
                    $prep = $this->SQL->conn->prepare("SELECT `file` FROM weather_data.camera WHERE station_hash = ? ORDER BY `id` DESC LIMIT 1");
                }
                $prep->bindParam(1, $_REQUEST['station_hash'], PDO::PARAM_STR);
                #$prep->bindParam(2, $_REQUEST['limit'], PDO::PARAM_INT);
                $prep->execute();
                $fetch = $prep->fetchAll(2);
                var_dump($fetch);
                break;
        }
    }
}