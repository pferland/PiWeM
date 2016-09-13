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
require $WWWconfig['http']['smarty_path']."Smarty.class.php"; #get smarty..

class PiWeMFront
{
    function __construct($WWWconfig = array())
    {
        if( @$WWWconfig['SQL'] == "" )
        {
            throw new Exception('$WWWconfig is not set!');
        }
        #now lets build the SQL class.
        $this->debug = 0;
        $this->SQL = new SQL($WWWconfig['SQL']);
        $this->smarty = new smarty();
#        $this->smarty->templates      = "/var/www/html/piwem/smarty/templates/";
#        $this->smarty->templates_c    = "/var/www/html/piwem/smarty/templates_c/" ;
#        $this->smarty->cache_dir      = "/var/www/html/piwem/smarty/cache/";
    }

    function GetStations()
    {
        $result = $this->SQL->conn->query("SELECT `station_name`, `station_hash` FROM `weather_data`.`Stations` ORDER BY id ASC");
        $fetch = $result->fetchall(2);
        return $fetch;
    }

    function GetStationInfo($station_hash)
    {
        $prep = $this->SQL->conn->prepare("SELECT `station_name`, `station_hash`, `lastupdate` FROM `weather_data`.`Stations` WHERE `station_hash` = ? ORDER BY id ASC");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $fetch = $prep->fetch(2);
        return $fetch;
    }

    function GetStationSensorData($station_hash = "", $sensor = "", $limit = 1)
    {
        $query_desc = "DESCRIBE `weather_data`.`$sensor`";
        if($this->debug)
        {
            var_dump($query_desc);
        }
        $result_desc = $this->SQL->conn->query($query_desc);
        $Desc_Fetch = $result_desc->fetchAll(2);
        if($this->debug)
        {
            var_dump($Desc_Fetch);
        }
        $not_zero_field = "";
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
            if($col['Field'] == "humidity")
            {
                $not_zero_field = "humidity";
            }elseif($col['Field'] == "pressure")
            {
                $no_zero_field = "pressure";
            }
            $t++;
        }

        $query .= "FROM `weather_data`.`$sensor` WHERE `station_hash` = '$station_hash' ";
        
        if($not_zero_field != "")
        {
            $query .= "AND `$not_zero_field` NOT LIKE 0 ";
        }

        $query .= "ORDER BY `id` DESC LIMIT $limit";

	
        if($this->debug)
        {
            var_dump($query);
        }


        $result_query = $this->SQL->conn->query($query);
        if($this->debug)
        {
            var_dump($result_query);
        }
        if ($result_query === false)
        {
            return 0;
        }
        $fetch = $result_query->fetchall(2);
        return $fetch;
    }


    function GetStationSensorDataAll($station_hash = "", $sensor = "")
    {
        if($this->debug)
        {
            var_dump($sensor);
        }
        $query_desc = "DESCRIBE `weather_data`.`$sensor`";
        #var_dump($query_desc);
        $result_desc = $this->SQL->conn->query($query_desc);
        $Desc_Fetch = $result_desc->fetchall(2);
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

        $query .= "FROM `weather_data`.`$sensor` WHERE `station_hash` = '$station_hash' ORDER BY `id` DESC";

        if($this->debug)
        {
            var_dump($query);
        }


        $result_query = $this->SQL->conn->query($query);
        #var_dump($result_query);
        if ($result_query === false)
        {
            return 0;
        }
        $fetch = $result_query->fetchall(2);

        return $fetch;
    }


    function GetStationSensors($station_hash = "")
    {
        $prep = $this->SQL->conn->prepare("SELECT dht11, dht22, bmp085, bmp180, bmp280, thermistor, analog_temp_sensor, photoresistor, camera FROM `weather_data`.`Station_sensors` WHERE station_hash = ? LIMIT 1");
        $prep->bindParam(1, $station_hash, PDO::PARAM_STR);
        $prep->execute();
        $fetch = $prep->fetch(2);
        if($this->debug) {
            var_dump($fetch);
        }
        return $fetch;
    }
}
