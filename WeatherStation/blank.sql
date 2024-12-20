USE `piwem_node`;

DROP TABLE IF EXISTS `am2302`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `am2302` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `humidity` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analog_temp_sensor`
--

DROP TABLE IF EXISTS `analog_temp_sensor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analog_temp_sensor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bmp085`
--

DROP TABLE IF EXISTS `bmp085`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bmp085` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pressure` float NOT NULL,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `altitude` float NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bmp180`
--

DROP TABLE IF EXISTS `bmp180`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bmp180` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pressure` float NOT NULL,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `altitude` float NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `bmp280`
--

DROP TABLE IF EXISTS `bmp280`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `bmp280` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pressure` float NOT NULL,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `altitude` float NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dht11`
--

DROP TABLE IF EXISTS `dht11`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dht11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `humidity` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `dht22`
--

DROP TABLE IF EXISTS `dht22`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `dht22` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `humidity` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `photoresistor`
--

DROP TABLE IF EXISTS `photoresistor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `photoresistor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `photolevel` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `power_monitor`
--

DROP TABLE IF EXISTS `power_monitor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `power_monitor` (
	`id` INT(255) NOT NULL AUTO_INCREMENT,
	`voltage` FLOAT NOT NULL,
	`shunt_mV` FLOAT NOT NULL,
	`current_mA` int(11) NOT NULL,
	`power_mW` FLOAT NOT NULL,
	`station_hash` VARCHAR(64) NOT NULL,
	`channel` INT(11) NOT NULL,
	`timestamp` VARCHAR(255) NOT NULL,

	`buffered_data` tinyint(4) DEFAULT '0',
	PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Table structure for table `thermistor`
--

DROP TABLE IF EXISTS `thermistor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `thermistor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `c_temp` int(11) NOT NULL,
  `f_temp` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;

--
-- Table structure for table `wind_speed`
--

DROP TABLE IF EXISTS `wind_speed`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wind_speed` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `miles_per_hour` float(3,2) NOT NULL,
  `meters_per_second` float(3,2) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;

--
-- Table structure for table `wind_direction`
--

DROP TABLE IF EXISTS `wind_direction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `wind_direction` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `direction` int(11) NOT NULL,
  `station_hash` varchar(64) NOT NULL,
  `timestamp` varchar(255) NOT NULL,
  `buffered_data` tinyint(4) DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;
