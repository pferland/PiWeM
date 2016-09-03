drop DATABASE weather_data;

create DATABASE weather_data;

CREATE TABLE weather_data.analog_temp_sensor
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.bmp085
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  pressure float(10) NOT NULL,
  altitude float(10) NOT NULL,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.bmp180
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  pressure float(10) NOT NULL,
  altitude float(10) NOT NULL,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.bmp280
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  pressure float(10) NOT NULL,
  altitude float(10) NOT NULL,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.dht11
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  humidity int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.dht22
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  humidity int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.Stations
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  station_name VARCHAR(255) NOT NULL,
  station_hash VARCHAR(64) UNIQUE KEY NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.Station_sensors
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  station_hash VARCHAR(64) NOT NULL,
  dht11 BOOLEAN NOT NULL,
  dht22 BOOLEAN NOT NULL,
  bmp085 BOOLEAN NOT NULL,
  bmp180 BOOLEAN NOT NULL,
  bmp280 BOOLEAN NOT NULL,
  thermistor BOOLEAN NOT NULL,
  analog_temp_sensor BOOLEAN NOT NULL,
  photoresistor BOOLEAN NOT NULL,
  camera BOOLEAN NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.photoresistor
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  photolevel int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);


CREATE TABLE weather_data.thermistor
(
  id int PRIMARY KEY NOT NULL AUTO_INCREMENT,
  c_temp int NOT NULL,
  f_temp int NOT NULL,
  station_hash VARCHAR(64) NOT NULL,
  timestamp VARCHAR(255) NOT NULL
);