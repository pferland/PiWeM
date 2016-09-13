<?php
/*
index.php
Copyright (C) 2013 Phil Ferland

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

require "lib/config.php"; #www config
require "lib/PiWeMFront.inc.php"; #PiWeM Front end class

#setup smarty
#init PiWeM Front end class
$PiWem_Front = new PiWeMFront($WWWconfig);

$stations = $PiWem_Front->GetStations();
$Stations_Data_Array = array();
foreach($stations as $station)
{
    $Stations_Data_Array[$station['station_hash']] = array();
    $Stations_Data_Array[$station['station_hash']]['station_name'] = $station['station_name'];
    $Stations_Data_Array[$station['station_hash']]['station_hash'] = $station['station_hash'];

    $sensors = $PiWem_Front->GetStationSensors($station['station_hash']);
    $Stations_Data_Array[$station['station_hash']]['sensors'] = array();
    foreach($sensors as $sensor=>$value)
    {
        if($value == "1")
        {
            if($PiWem_Front->debug)
            {
                var_dump($sensor);
            }

            $Stations_Data_Array[$station['station_hash']]['sensors'][$sensor] = $PiWem_Front->GetStationSensorData($station['station_hash'], $sensor, 1);
        }
    }
}
if($PiWem_Front->debug)
{
    var_dump($Stations_Data_Array);
}

if(!$PiWem_Front->debug)
{
    $PiWem_Front->smarty->assign("stations", $Stations_Data_Array);
    $PiWem_Front->smarty->display("index.tpl");
}

