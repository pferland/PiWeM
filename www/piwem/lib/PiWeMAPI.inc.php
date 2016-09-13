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

        $this->station_name = "";
        $this->station_hash = "";
        $this->station_key = "";
    }

    function checkapikey()
    {
        $prep = $this->SQL->conn->prepare("SELECT station_name FROM `weather_data`.`Stations` WHERE station_hash = ? AND station_key = ?");
        $prep->bindParam(1, $this->station_hash, PDO::PARAM_STR);
        $prep->bindParam(2, $this->station_key, PDO::PARAM_STR);
        $prep->execute();
        $result = $prep->fetch(2);
        var_dump($result);
    }
}