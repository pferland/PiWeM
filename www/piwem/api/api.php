<?php

require "../lib/config.php";
#var_dump($WWWconfig);

require "../lib/PiWeMAPI.inc.php";



$PiWeMAPI = new PiWeMAPI($WWWconfig);

$PiWeMAPI->station_hash = $_REQUEST['station_hash'];
$PiWeMAPI->station_key = $_REQUEST['station_key'];

if(!$PiWeMAPI->checkapikey())
{
    exit("Invalid Station or Key.");
}


switch(strtolower(@$_REQUEST['mode']))
{
    case "importdata":
        $PiWeMAPI->payload = $_REQUEST['payload'];
        $PiWeMAPI->importdata();
        break;

#    case "import_picture":
#        $PiWeMAPI->import_picture();
#        break;

    default:

        break;
}