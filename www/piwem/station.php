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
$Station_Data_Array = array();

$station = $PiWem_Front->GetStationInfo($_REQUEST['station_hash']);

$Station_Data_Array['station_name'] = $station['station_name'];
$Station_Data_Array['station_hash'] = $station['station_hash'];

$sensors = $PiWem_Front->GetStationSensors($Station_Data_Array['station_hash']);

foreach($sensors as $sensor=>$value)
{
    $flag = (int)$value;
    if ($PiWem_Front->debug) {
        var_dump($sensor);
        var_dump($flag);
    }
    if(!$flag)
    {
        continue;
    }
    $Station_Data_Array['sensors'][$sensor]['name'] = $sensor;
    $Station_Data_Array['sensors'][$sensor]['data'] = $PiWem_Front->GetStationSensorData($Station_Data_Array['station_hash'], $sensor, 100);
}

if(!$PiWem_Front->debug)
{
    $PiWem_Front->smarty->assign("stations", $stations);
    $PiWem_Front->smarty->assign("station_data", $Station_Data_Array);
    $PiWem_Front->smarty->display("station.tpl");
}

