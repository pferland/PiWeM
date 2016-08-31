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

require "lib/SQL.php"; #the uh.. SQL class...
class PiWeMFront
{

    function __construct($WWWconfig = array())
    {
        if( @$WWWconfig['SQL'] == "" )
        {
            throw new Exception('$WWWconfig is not set!');
        }
        #now lets build the SQL class.
        $this->SQL = new SQL($WWWconfig['SQL']);
    }

    function GetStations()
    {
        $result = $this->SQL->conn->query("SELECT `id`, `station_name`, `station_hash` FROM `weather_data`.`Stations` ORDER BY id ASC");
        $fetch = $result->fetchall(2);
        return $fetch;
    }

    function GetStationSensorData($station_hash = "", $sensor = "")
    {
        $query_desc = "DESCRIBE `weather_data`.`$sensor`";
        #var_dump($query_desc);
        $result_desc = $this->SQL->conn->query($query_desc);
        $Desc_Fetch = $result_desc->fetchAll(2);
        #var_dump($Desc_Fetch);
        $query = "SELECT ";
        $t = 0;
        foreach($Desc_Fetch as $col)
        {
            if($col['Field'] == "id" || $col['Field'] == "station_hash")
            {
                continue;
            }
            if($t == 0)
            {
                $query .= $col['Field'];
            }else
            {
                $query .= ", ".$col['Field']." ";
            }
            $t++;
        }

        $query .= "FROM `weather_data`.`$sensor` WHERE `station_hash` = '$station_hash' ORDER BY `id` DESC LIMIT 1";

        #var_dump($query);

        $result_query = $this->SQL->conn->query($query);
        #var_dump($result_query);
        if ($result_query === false)
        {
            return 0;
        }
        $fetch = $result_query->fetch(2);

        return $fetch;
    }

    function GetStationSensors($station_hash = "")
    {
        $prep = $this->SQL->conn->prepare("SELECT dht11, dht22, bmp085, bmp180, bmp280, thermistor, analog_temp_sensor, photoresistor FROM `weather_data`.`Station_sensors` WHERE station_hash = ?");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $fetch = $prep->fetch(2);

        return $fetch;
    }
}