USE `piwem_cs`;

DROP TABLE IF EXISTS `Station_sensors`;

CREATE TABLE `Station_sensors` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `station_hash` varchar(64) NOT NULL,
  `dht11` tinyint(1) NOT NULL,
  `dht22` tinyint(1) NOT NULL,
  `bmp085` tinyint(1) NOT NULL,
  `bmp180` tinyint(1) NOT NULL,
  `bmp280` tinyint(1) NOT NULL,
  `thermistor` tinyint(1) NOT NULL,
  `analog_temp_sensor` tinyint(1) NOT NULL,
  `photoresistor` tinyint(1) NOT NULL,
  `camera` tinyint(1) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `am2302` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `Stations`;

CREATE TABLE `Stations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `station_name` varchar(255) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `lastupdate` varchar(32) DEFAULT NULL,
  `station_key` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `station_hash` (`station_hash`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;


DROP TABLE IF EXISTS `weather_data`;

CREATE TABLE `weather_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pressure` float NOT NULL,
  `altitude` float NOT NULL,
  `photolevel` int(11) NOT NULL,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `humidity` int(11) NOT NULL,
  `voltage` FLOAT NOT NULL,
  `shunt_mV` FLOAT NOT NULL,
  `current_mA` int(11) NOT NULL,
  `power_mW` FLOAT NOT NULL,
  `power_channel` INT(11) NOT NULL,
  `wind_mps` float(3,2) NOT NULL,
  `wind_direction` int(11) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
