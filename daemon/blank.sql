CREATE TABLE weather_data.analog_temp_sensor
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.bmp085
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  pressure float(10) NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.bmp180
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  pressure float(10) NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.bmp280
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  pressure float(10) NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.dht11
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  humidity int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.dht22
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  humidity int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.Stations
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  station_name VARCHAR(255) NOT NULL,
  station_hash VARCHAR(64) UNIQUE KEY NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.Station_sensors
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  station_hash VARCHAR(64) NOT NULL,
  dht11 TINYINT(1) NOT NULL,
  dht22 TINYINT(1) NOT NULL,
  bmp085 TINYINT(1) NOT NULL,
  bmp180 TINYINT(1) NOT NULL,
  bmp280 TINYINT(1) NOT NULL,
  thermistor TINYINT(1) NOT NULL,
  analog_temp_sensor TINYINT(1) NOT NULL,
  photoresistor TINYINT(1) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.photoresistor
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  photolevel int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);


CREATE TABLE weather_data.thermistor
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp int NOT NULL
);

