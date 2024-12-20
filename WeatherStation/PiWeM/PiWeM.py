from pprint import pprint
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import RPi.GPIO as GPIO
import datetime
import json
import math
import os
import socket
import sys
import uuid
import urllib
import urllib2

# PiWeM Packages
import Payload
from SensorData import SensorValues
from wind import wind
from power import power

# Yeah.. Yeah.. I know...
global sensor

class PIWEM:
    # Really just for the daemon to keep track of loop numbers during error loops, but its what number you want it to start counting at.
    loop_int        = 0

    # This stations Hash, it should be generated on the first run and saved to the DB and the station_hash.txt file
    station_hash             = ""
    station_key              = ""
    station_name             = ""
    payload                  = None
    json_data                = ""
    PiWem_Central_Server     = ""
    Upload_To_Central_Server = 0
    localstorage             = 0
    bufferlocally            = 0
    buffered_data            = 0

    #Where you want the weather data to be logged to. so far just supports CSV and TSV Well not really, but it will be
    sql_log_data    = 0
    file_log        = 0
    file_log_type   = 'csv'  # supports csv or tsv (comma or tab)

    # write values to the console
    verbose     = 0

    #used to get much more data about what is happening, really only needed if you are fucking around with the code. Might get some nifty information ;-)
    debug       = 0

    #Enable or disables devices.
    pcf8591_enabled             = 0
    am2302_enabled              = 0
    bmp085_enabled              = 0
    bmp180_enabled              = 0
    bmp280_enabled              = 0
    dht11_enabled               = 0
    dht22_enabled               = 0
    thermistor_enabled          = 0
    analog_temp_sensor_enabled  = 0
    photoresistor_enabled       = 0
    camera_enabled              = 0

    # GPIO Pins for devices
    dht11_pin   = 0
    dht22_pin   = 0
    am2302_pin  = 0
    ds18b20_pin = 0

    #Init values for the DHT sensors. Supports both the DHT11 and DHT22. Others will be added when I find and can buy other devices.
    dht11_instance  = None
    dht22_instance  = None
    am2302_instance = None

    # Initial Values for Wind Sensors
    wind_enabled                   = 0
    anemometer_sensor_diameter     = 0
    analog_wind_anemometer_enabled = 0
    analog_wind_vane_enabled       = 0
    analog_wind_anemometer_pin     = 0
    analog_wind_vane_pin           = 0


    # RasPi camera settings, defaults should work for both v1 and v2 of the camera
    camera              = None
    brightness          = 50
    resolution          = (1920,1080)
    jpeg_quality        = 100
    text_font           = ""
    text_color          = (255,0,0)
    output_path         = ""
    tmp_dir             = ""

    #Init values for the SQL connection only need the DB and conn, others are not needed to be static, can just grab them again from the settings var.
    db   = None
    conn = None

    #PCF8591 Analog to Digital switcher init, address, and device settings, address up to 4 devices at once.
    pcf8591_instance        = None
    pcf8591_address         = -1
    photosresistor_channel  = -1
    ats_channel             = -1
    thermistor_channel      = -1

    #BPM085 Barometer pressure sensor init and address
    bmp085_instance    = None
    bmp085_address     = 0x77

    #BPM180 Barometer pressure sensor init and address
    bmp180_instance    = None
    bmp180_address     = 0x77

    #BPM280 Barometer pressure sensor init and address
    bmp280_instance    = None
    bmp280_address     = 0x76

    sensor_values = None

    def __init__(self, settings=[]):
        if not settings:
            raise ValueError("PiWeM settings argument was not set...")

        # initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()

        self.station_name = socket.gethostname()
        self.verbose = int(settings['verbose'])
        self.debug = int(settings['debug'])
        self.__settings = settings
        self.localstorage = int(settings['localstorage'])
        self.bufferlocally = int(settings['bufferlocally'])

        self.upload_to_weather_underground = int(settings['upload_to_weather_underground'])
        self.wu_url = settings['wu_url']
        self.wu_station_id = settings['wu_station_id']
        self.wu_station_key = settings['wu_station_key']

        self.temp_flag = settings['temp_flag']
        self.pressure_flag = settings['pressure_flag']
        self.humidity_flag = settings['humidity_flag']

        self.power_monitor = int(settings['power_monitor'])
        self.camera_enabled = int(settings['camera_enabled'])
        self.bmp085_enabled = int(settings['bmp085_enabled'])
        self.bmp180_enabled = int(settings['bmp180_enabled'])
        self.bmp280_enabled = int(settings['bmp280_enabled'])
        self.dht11_enabled = int(settings['dht11_enabled'])
        self.dht22_enabled = int(settings['dht22_enabled'])
        self.am2302_enabled = int(settings['am2302_enabled'])
        self.pcf8591_enabled = int(settings['pcf8591_enabled'])
        self.thermistor_enabled = int(settings['thermistor_enabled'])
        self.analog_temp_sensor_enabled = int(settings['analog_temp_sensor_enabled'])
        self.photoresistor_enabled = int(settings['photoresistor_enabled'])
        self.analog_wind_anemometer_enabled = int(settings['analog_wind_anemometer_enabled'])
        self.analog_wind_vane_enabled = int(settings['analog_wind_vane_enabled'])
        self.wind_enabled = int(settings['wind_enabled'])
        self.anemometer_sensor_diameter = float(settings['anemometer_sensor_diameter'])
        if self.debug:
            print "-----------------------------"
            pprint(settings)
            print "-----------------------------"

        if self.localstorage or self.bufferlocally:
            if self.verbose:
                print "Open MySQL Connection.."

            import MySQLdb
            self.db = MySQLdb.connect(host=settings['sql_host'], user=settings['sql_user'], passwd=settings['sql_password'])
            self.conn = self.db.cursor()
            if self.verbose:
                self.conn.execute("SHOW VARIABLES LIKE '%version%'")
                ret = self.conn.fetchall()
                if self.debug:
                    pprint(ret)
            # Check for and/or generate station hash and write it to a file.
            self.get_station_hash()
            self.get_station_key()
            if self.debug:
                print "Station Hash: " + self.station_hash
                print "Station Key: " + self.station_key
        self.loop_int = 0
        self.sleep_time = int(settings['sleep_time'])
        self.power_monitor_device = settings['power_monitor_device']

        self.INA219_address = int(settings['ina219_address'], 16)
        self.INA3221_address = int(settings['ina3221_address'], 16)

        self.am2302_pin = settings['am2302_pin']
        self.dht11_pin = settings['dht11_pin']
        self.dht22_pin = settings['dht22_pin']
        self.ds18b20_pin = settings['ds18b20_pin']

        self.bmp085_address = int(settings['bmp085_address'], 16)
        self.bmp180_address = int(settings['bmp180_address'], 16)
        self.bmp280_address = int(settings['bmp280_address'], 16)

        self.pcf8591_address = int(settings['pcf8591_address'], 16)
        self.thermistor_channel = settings['thermistor_channel']
        self.photosresistor_channel = int(settings['photoresistor_channel'])  # Photoresistor on the PCF8591 channel 0
        self.ats_channel = int(settings['ats_channel'])

        self.analog_wind_vane_pin = int(settings['analog_wind_vane_pin'])
        self.analog_wind_anemometer_pin = int(settings['analog_wind_anemometer_pin'])

        self.brightness = int(settings['brightness'])
        res = settings['resolution'].split(",")
        self.resolution = int(res[0]), int(res[1])
        self.rotation = int(settings['rotation'])
        self.jpeg_quality = int(settings['jpeg_quality'])
        self.text_font = settings['text_font']
        self.output_path = settings['output_path']

        self.PiWem_Central_Server = settings['piwem_central_server']
        self.Upload_To_Central_Server = int(settings['upload_to_central_server'])

        self.sensor_values = SensorValues.SensorValues()
        self.setup_sensors()

        if self.localstorage or self.bufferlocally:
            self.update_station_sensors()

        self.power = power.power(sql_db=MySQLdb.connect(host=settings['sql_host'], user=settings['sql_user'], passwd=settings['sql_password']),
                                 power_monitor=self.power_monitor, power_monitor_device=self.power_monitor_device,
                                 INA219_address=self.INA219_address, INA3221_address=self.INA3221_address, debug=self.debug, verbose=self.verbose)
        self.wind = wind.wind(anemometer_sensor_diameter=self.anemometer_sensor_diameter, analog_wind_vane_pin=self.analog_wind_vane_pin, analog_wind_anemometer_pin=self.analog_wind_anemometer_pin, debug=0, verbose=self.verbose)
        if self.get_station_key() == "":
            if self.verbose:
                print("Updating Station Key")
            self.update_station_key()
            if self.debug:
                print("New Station Key: " + self.station_key)

        #sys.exit(1)

    def get_station_hash(self):
        if not os.path.isfile("station_hash.txt"):
            if self.verbose:
                print "station_hash.txt did not exist. needed to generate a Station Hash. You will need to register"
            station_hash = self.genhash()
            self.station_hash = station_hash
        else:
            station_hash_file = open('station_hash.txt', 'r')
            self.station_hash = station_hash_file.read()
            station_hash_file.close()
        return self.station_hash

    def get_station_key(self):
        self.conn.execute("select `station_key` from weather_data.Stations where station_hash = %s", self.station_hash)
        ret = self.conn.fetchall()
        self.station_key = ret[0][0]
        return self.station_key

    def update_station_key(self):
        station_key_file = open('station_key.txt', 'w+')
        self.station_key = str(uuid.uuid4())
        station_key_file.write(self.station_key)
        station_key_file.close()

        self.conn.executemany(
            "UPDATE `weather_data`.`Stations` SET station_key = %s WHERE station_hash = %s",
            [
                (self.station_key, self.station_hash),
            ])
        self.db.commit()
        return self.station_key

    def genhash(self):
        station_hash_file = open('station_hash.txt', 'w+')
        self.station_hash = str(uuid.uuid4())
        station_hash_file.write(self.station_hash)
        station_hash_file.close()
        return self.station_hash

    def setup_sensors(self):
        self.setup_dht11(pin=int(self.dht11_pin))
        self.setup_dht22(pin=int(self.dht22_pin))
        self.setup_am2302(pin=int(self.am2302_pin))

        self.setup_bmp085(address=self.bmp085_address)  #  Low (ground) on sda for the BMP is 0x76, High is 0x77
        self.setup_bmp180(address=self.bmp180_address)  #  Temp til I get a 180 to test with.)
        self.setup_bmp280(address=self.bmp280_address)

        self.setup_pcf8591(address=self.pcf8591_address)  # Default address for the PCF8591 is 0x48, so its hardcoded, but you can set it to what ever you want with the address variable
        self.setup_camera()

    def insert_station_sensors(self):
        timestamp = str(datetime.datetime.utcnow())

        if self.debug:
            print "Values to write to sensor tables:"
            print (self.station_hash, bool(self.dht11_enabled), bool(self.dht22_enabled), bool(self.bmp085_enabled), bool(self.bmp180_enabled), bool(self.bmp280_enabled), bool(self.thermistor_enabled), bool(self.analog_temp_sensor_enabled), bool(self.photoresistor_enabled), bool(self.camera_enabled), timestamp)
            print ""
        self.conn.executemany("INSERT INTO `weather_data`.`Station_sensors` (`station_hash`, `dht11`, `dht22`, `bmp085`, `bmp180`, `bmp280`, `thermistor`, `analog_temp_sensor`, `photoresistor`, `camera`, `timestamp`)  "
                              "VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ",
        [
            (self.station_hash, bool(self.dht11_enabled), bool(self.dht22_enabled), bool(self.bmp085_enabled), bool(self.bmp180_enabled), bool(self.bmp280_enabled), bool(self.thermistor_enabled), bool(self.analog_temp_sensor_enabled), bool(self.photoresistor_enabled), bool(self.camera_enabled), timestamp),
        ])
        self.db.commit()
        return 0

    def update_station_sensors(self):
        self.conn.executemany("UPDATE weather_data.Station_sensors SET bmp085 = %s, bmp180 = %s, bmp280 = %s, dht11 = %s, dht22 = %s, am2302 = %s, thermistor = %s, analog_temp_sensor = %s, photoresistor = %s, camera = %s "
                              "WHERE station_hash = %s ",
        [
            (self.bmp085_enabled, self.bmp180_enabled, self.bmp280_enabled, self.dht11_enabled, self.dht22_enabled, self.am2302_enabled, self.thermistor_enabled, self.analog_temp_sensor_enabled, self.photoresistor_enabled, self.camera_enabled, self.station_hash),
        ])
        self.db.commit()
        return 0

    def insert_station(self):
        timestamp = str(datetime.datetime.utcnow())
        self.conn.executemany("INSERT INTO weather_data.Stations ( station_hash, station_key, station_name, `timestamp` ) VALUES ( %s, %s, %s, %s) ",
        [
            (self.station_hash, self.station_key, self.station_name, timestamp),
        ])
        self.db.commit()
        return 0

    def setup_bmp085(self, address = 0x77):
        if self.bmp085_enabled:
            import Adafruit_BMP.BMP085 as BMP085
            self.bmp085_address = address
            self.bmp085_instance = BMP085.BMP085(address=self.bmp085_address)
        return 0

    def setup_bmp180(self, address = 0x77):
        if self.bmp180_enabled:
            import Adafruit_BMP.BMP085 as BMP085
            self.bmp180_address = address
            self.bmp180_instance = BMP085.BMP085(address=self.bmp180_address, mode=BMP085.BMP085_ULTRAHIGHRES)
        return 0

    def setup_bmp280(self, address = 0x76):
        if self.bmp280_enabled:
            import bmp280 as bmp280_sn
            self.bmp280_address = address
            self.bmp280_instance = bmp280_sn.bmp280(address=self.bmp280_address)
        return 0

    def setup_pcf8591(self, address = 0x48):
        if self.pcf8591_enabled:
            import PCF8591 as ADC
            self.pcf8591_address = address
            self.pcf8591_instance = ADC
            self.pcf8591_instance.setup(self.pcf8591_address)
        return 0

    def setup_dht11(self, pin):
        if self.dht11_enabled:
            from dht11 import dht11
            self.dht11_pin      = pin
            self.dht11_instance = dht11.DHT11(pin=self.dht11_pin)
        return 0

    def setup_dht22(self, pin):
        if self.dht22_enabled:
            from dht11 import dht11
            self.dht22_pin = pin
            self.dht22_instance = dht11.DHT11(pin=self.dht22_pin)   # will add after the dht22 order comes in :/ ...
        return 0

    def setup_am2302(self, pin):
        if self.am2302_enabled:
            from dht11 import dht11
            self.am2302_pin = pin
            self.am2302_instance = dht11.DHT11(pin=self.am2302_pin)
            #self.am2302_instance = DHT   # will add after the dht22 order comes in :/ ...
        return 0

    def setup_camera(self):
        if self.camera_enabled:
            import picamera
            self.camera             = picamera.PiCamera()
            self.camera.rotation    = self.rotation
            self.camera.brightness  = self.brightness
            self.camera.resolution  = self.resolution
        return 0

    def insert_data(self, buffered=0):
        if self.debug:
            print "--------- Insert Data values for self.sensor_values.*  ------------"
            print ""
            print "BMP085 Temp/Pressure"
            print self.sensor_values.bmp085.temp
            print self.sensor_values.bmp085.pressure

            print "BMP180 Temp/Pressure"
            print self.sensor_values.bmp180.temp
            print self.sensor_values.bmp180.pressure

            print "BMP280 Temp/Pressure"
            print self.sensor_values.bmp280.temp
            print self.sensor_values.bmp280.pressure

            print "DHT11 Temp/Humidty"
            print self.sensor_values.dht11.temp
            print self.sensor_values.dht11.humidity

            print "DHT22 Temp/Humidty"
            print self.sensor_values.dht22.temp
            print self.sensor_values.dht22.humidity

            print "Thermistor Temperature"
            print self.sensor_values.thermistor

            print "Analog Temperature Sensor"
            print self.sensor_values.analog_temp_sensor

            print "Photoresistor"
            print self.sensor_values.photoresistor

            print "Wind Speed"
            print self.sensor_values.wind_speed

            print "Wind Direction"
            print self.sensor_values.wind_direction

            print "Fetch Error Result Flag"
            if self.sensor_values.fetch_error:
                print self.sensor_values.fetch_error
            print "-------------------------------------------------------------------"

        if self.bmp085_enabled:
            if self.debug:
                print "bmp085_enabled"
            self.conn.executemany("INSERT INTO weather_data.bmp085 ( pressure, c_temp, f_temp, altitude, station_hash, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.bmp085.pressure, self.sensor_values.bmp085.temp[0], self.sensor_values.bmp085.temp[1], self.sensor_values.bmp085.altitude, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.bmp180_enabled:
            if self.debug:
                print "bmp180_enabled"
            self.conn.executemany("INSERT INTO weather_data.bmp180 ( pressure, c_temp, f_temp, altitude, station_hash, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.bmp180.pressure, self.sensor_values.bmp180.temp[0], self.sensor_values.bmp180.temp[1], self.sensor_values.bmp180.altitude, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.bmp280_enabled:
            if self.debug:
                print "bmp280_enabled"
                print self.sensor_values.bmp280.pressure
                print self.sensor_values.bmp280.temp
            self.conn.executemany("INSERT INTO weather_data.bmp280 ( pressure, c_temp, f_temp, altitude, station_hash, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.bmp280.pressure, self.sensor_values.bmp280.temp[0], self.sensor_values.bmp280.temp[1], self.sensor_values.bmp280.altitude, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.dht11_enabled:
            if self.debug:
                print "dht11_enabled"
            self.conn.executemany("INSERT INTO weather_data.dht11 ( c_temp, f_temp, humidity, station_hash, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.dht11.temp[0], self.sensor_values.dht11.temp[1], self.sensor_values.dht11.humidity, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.dht22_enabled:
            if self.debug:
                print "dht22_enabled"
            self.conn.executemany("INSERT INTO weather_data.dht22 ( c_temp, f_temp, humidity, station_hash, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.dht22.temp[0], self.sensor_values.dht22.temp[1], self.sensor_values.dht22.humidity, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.thermistor_enabled:
            if self.debug:
                print "thermistor_enabled"
            self.conn.executemany("INSERT INTO weather_data.thermistor ( c_temp, f_temp, station_hash, `timestamp`, `buffered_data` ) VALUES (%s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.thermistor[0], self.sensor_values.thermistor[1], self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.analog_temp_sensor_enabled:
            if self.debug:
                print "analog_temp_sensor_enabled"
            self.conn.executemany("INSERT INTO weather_data.analog_temp_sensor ( c_temp, f_temp, station_hash, `timestamp`, `buffered_data` ) VALUES (%s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.analog_temp_sensor[0], self.sensor_values.analog_temp_sensor[1], self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.photoresistor_enabled:
            if self.debug:
                print "photoresistor_enabled"
            self.conn.executemany("INSERT INTO weather_data.photoresistor ( `photolevel`, `station_hash`, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s) ",
            [
                (self.sensor_values.photoresistor, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.analog_wind_anemometer_enabled:
            if self.debug:
                print "analog_wind_anemometer_enabled"
            self.conn.executemany("INSERT INTO weather_data.wind_speed ( `miles_per_hour`, `meters_per_second`, `station_hash`, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s, %s) ",
            [
                (self.sensor_values.wind_speed[0], self.sensor_values.wind_speed[1], self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.analog_wind_vane_enabled:
            if self.debug:
                print "analog_wind_vane_enabled"
            self.conn.executemany("INSERT INTO weather_data.wind_direction ( `direction`, `station_hash`, `timestamp`, `buffered_data` ) VALUES ( %s, %s, %s, %s) ",
            [
                (self.sensor_values.wind_direction, self.station_hash, self.sensor_values.timestamp, buffered),
            ])
            self.db.commit()

        if self.power_monitor:
            if self.debug:
                print "power monitor data"

            insert_array = []
            for i in range(len(self.sensor_values.power)):
                insert_array.append((self.station_hash, i, self.sensor_values.power[i].shunt_mV, self.sensor_values.power[i].voltage,
                 self.sensor_values.power[i].current_mA, self.sensor_values.power[i].power_mW,
                 self.sensor_values.timestsamp))

            self.conn.executemany(
                "INSERT INTO weather_data.power_monitor ( station_hash, `channel`, `shunt_mV`, `voltage`, `current_mA`, "
                "`power_mW`, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s, %s) ",
                insert_array
            )
            self.db.commit()
        return 0

    def get_cpu_temperature(self):
        res = os.popen('vcgencmd measure_temp').readline()
        return(res.replace("temp=","").replace("'C\n",""))

    def get_am2302_data(self):
        if self.am2302_enabled:
            result = self.am2302_instance.read()
            f_temp = ((int(result.temperature) * 9)/5)+32
            print result
            if result.humidity is 0:
                print "Error fetching DHT Data"
                humidity_results = 0
            else:
                humidity_results = result.humidity
            if result.temperature is 0:
                temp_results = (0, 0)
                self.sensor_values.fetch_error.append("AM2302 fetch error")
            else:
                temp_results = (result.temperature, f_temp)
            return temp_results, humidity_results
        return 0

    def get_dht11_data(self):
        if self.dht11_enabled:
            result = self.dht11_instance.read()
            f_temp = ((int(result.temperature) * 9)/5)+32
            if result.humidity is 0:
                if self.debug:
                    print "Error fetching DHT Data"
                humidity_results = 0
            else:
                humidity_results = result.humidity
            if result.temperature is 0:
                temp_results = (0, 0)
                self.sensor_values.fetch_error.append("DHT11 fetch error")
            else:
                temp_results = (result.temperature, f_temp)
            return temp_results, humidity_results
        return 0

    def get_dht22_data(self):
        if self.dht11_enabled:
            result = self.dht11_instance.read()
            f_temp = ((int(result.temperature) * 9)/5)+32
            if result.humidity is 0:
                if self.debug:
                    print "Error fetching DHT Data"
                humidity_results = 0
            else:
                humidity_results = result.humidity
            if result.temperature is 0:
                temp_results = (0, 0)
                self.sensor_values.fetch_error.append("DHT11 fetch error")
            else:
                temp_results = (result.temperature, f_temp)
            return temp_results, humidity_results
        return 0

    def get_bmp085_data(self):
        if self.bmp085_enabled:
            pressure = self.bmp085_instance.read_pressure()       # Read pressure to variable pressure
            if pressure is 0:
                self.sensor_values.fetch_error.append("BMP085 pressure fetch error")
                raise IOError("Fetching Data Error BMP085 Pressure...")

            temp = self.bmp085_instance.read_temperature()        # Read temperature to variable temp
            if temp is 0:
                self.sensor_values.fetch_error.append("bmp085 temperature fetch error")
                raise IOError("Fetching Data Error BMP085 Temperature...")

            f_temp = ((int(temp) * 9)/5)+32

            alt = self.bmp085_instance.read_altitude()

            return (temp, f_temp), pressure, alt
        return 0

    def get_bmp280_data(self):
        if self.bmp280_enabled:
            data = self.bmp280_instance.read()
            if data[0] is 0:
                raise IOError("BMP280 did not return any valid data.")
            return data

    def get_bmp180_data(self):
        if self.bmp180_enabled:
            data = self.bmp180_instance.read()
            if data[0] is 0:
                raise IOError("BMP180 did not return any valid data.")
            return data

    def get_thermistor_temp_data(self):   # Get Data from the Thermistor
        if self.thermistor_enabled:
            if self.debug:
                print "Thermistor Channel: "+ str(self.thermistor_channel)
            analogVal = self.pcf8591_instance.read(self.thermistor_channel)
            if self.debug:
                print "Analog Value for Thermistor: " + str(analogVal)
            if analogVal is 255:
                self.sensor_values.fetch_error.append("Thermistor result value error")
                return 0, 0
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
            temp = temp - 273.15
            f_temp = ((int(temp) * 9)/5)+32
            if self.debug:
                print "Celsius: " + str(temp) + " ||  Fahrenheit" + str(f_temp)
            #sys.exit(1)
            return temp, f_temp
        return 0

    def get_ats_temp_data(self):  # Get data from the Analog Temperature Sensor
        if self.analog_temp_sensor_enabled:
            if self.debug:
                print "ATS Channel: "+ str(self.ats_channel)
            analogVal = self.pcf8591_instance.read(self.ats_channel)
            if self.debug:
                print "Analog Value for ATS: " + str(analogVal)
            if analogVal is 255:
                self.sensor_values.fetch_error.append("Analog Temperature Sensor value return error")
                return 0, 0
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
            temp = temp - 273.15
            f_temp = ((int(temp) * 9)/5)+32
            if self.debug:
                print "Analog C Temp: " + str(temp) + "    Analog F Temp" + str(f_temp)
            #sys.exit(1)
            return temp, f_temp
        return 0

    def get_sensor_data(self):  # Gather all of the sensors data

        if self.verbose:
                sys.stdout.write("Polling: ")
                sys.stdout.flush()
        self.sensor_values.timestamp = str(datetime.datetime.utcnow())

        if self.bmp085_enabled:
            if self.verbose:
                sys.stdout.write("bmp085")
                sys.stdout.flush()
            try:
                bmp085_data = self.get_bmp085_data()
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])

            self.sensor_values.bmp085.temp = bmp085_data[0]
            self.sensor_values.bmp085.pressure = bmp085_data[1]
            self.sensor_values.bmp085.altitude = bmp085_data[2]

        if self.bmp180_enabled:
            if self.verbose:
                sys.stdout.write(", bmp180")
            sys.stdout.flush()
            try:
                bmp180_data = self.get_bmp180_data()
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])
            self.sensor_values.bmp180.temp = bmp180_data[0]
            self.sensor_values.bmp180.pressure = bmp180_data[1]

        if self.bmp280_enabled:
            if self.verbose:
                sys.stdout.write(", bmp280")
                sys.stdout.flush()
            try:
                bmp280_data = self.get_bmp280_data()
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])
            self.sensor_values.bmp280.temp = bmp280_data[0]
            self.sensor_values.bmp280.pressure = bmp280_data[1]
            self.sensor_values.bmp280.altitude = bmp280_data[2]

        if self.thermistor_enabled:
            if self.verbose:
                sys.stdout.write(", Thermistor")
                sys.stdout.flush()
            try:
                self.sensor_values.thermistor = self.get_thermistor_temp_data()
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])

        if self.analog_temp_sensor_enabled:
            if self.verbose:
                sys.stdout.write(", ATS")
                sys.stdout.flush()
            try:
                self.sensor_values.analog_temp_sensor = self.get_ats_temp_data()
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])

        if self.dht11_enabled:
            if self.verbose:
                sys.stdout.write(", dht11")
                sys.stdout.flush()
            try:
                dht11_data = self.get_dht11_data()
                self.sensor_values.dht11.temp = dht11_data[0]
                self.sensor_values.dht11.humidity = dht11_data[1]
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])

        if self.dht22_enabled:
            if self.verbose:
                sys.stdout.write(", dht22")
                sys.stdout.flush()
            try:
                dht22_data = self.get_dht22_data()
                self.sensor_values.dht22.temp = dht22_data[0]
                self.sensor_values.dht22.humidity = dht22_data[1]
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])

        if self.photoresistor_enabled:
            if self.verbose:
                sys.stdout.write(", Photoresistor")
                sys.stdout.flush()
            try:
                self.sensor_values.photoresistor = self.get_photolevel_data()
            except:
                self.sensor_values.fetch_error.append(sys.exc_info()[0])

        if self.wind_enabled:
            if self.analog_wind_vane_enabled:
                if self.verbose:
                    sys.stdout.write(", Wind Vane")
                    sys.stdout.flush()
                    try:
                        self.sensor_values.wind_direction = self.wind.getDirection()
                    except:
                        self.sensor_values.fetch_error.append(sys.exc_info()[0])

            if self.analog_wind_anemometer_enabled:
                if self.verbose:
                    sys.stdout.write(", Wind Anemometer")
                    sys.stdout.flush()
                try:
                    self.sensor_values.wind_speed = self.wind.getWindSpeedData()
                except:
                    self.sensor_values.fetch_error.append(sys.exc_info()[0])

        if self.power_monitor:
            power_values = self.power.getpower()
            for i in range(len(power_values)):
                self.sensor_values.power[i].channel = power_values[i][0]
                self.sensor_values.power[i].current_mA = power_values[i][1]
                self.sensor_values.power[i].power_mW = power_values[i][2]
                self.sensor_values.power[i].shunt_mV = power_values[i][3]
                self.sensor_values.power[i].voltage = power_values[i][4]

        if self.verbose:
            sys.stdout.write("\r\n")
            sys.stdout.flush()
        return 1

    # Get levels from the Photoresistor
    def get_photolevel_data(self):
        if self.photoresistor_enabled:
            photo_level = self.pcf8591_instance.read(self.photosresistor_channel)
            if self.debug:
                print "PhotoLevel: " + str(photo_level)
            return photo_level
        return 0

    def take_picture(self):   # well i think this is self-explanatory...
        if self.debug:
            print("Take Picture.")
        image_name = self.tmp_dir + "Image_" + str(datetime.datetime.utcnow()) + ".jpg"
        self.camera.capture(image_name)
        return image_name

    def check_for_buffered_data(self):
        self.conn.executemany("SELECT buffered_data FROM `weather_data`.`Stations` WHERE `station_hash` = %s", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return data[0][0]

    def get_data_trigger(self):  #Main loop trigger and handler for the daemon
        if self.verbose:
            print "Get Sensor Data."
        self.get_sensor_data()

#        if not self.sensor_values.fetch_error:
        if self.localstorage:
            if self.verbose:
                print "Save data locally."
            self.insert_data()

        if self.Upload_To_Central_Server:
            if self.verbose:
                print "Upload data to the Central Server."
            ret = self.upload_data()
            if ret is -1:
                if self.bufferlocally:
                    if self.verbose:
                        print "Failed upload to " + self.PiWem_Central_Server + " Buffering data locally for now."
                    self.set_buffered_data(1)
                    self.insert_data(1)
            else:
                if self.verbose:
                    print "Upload Successful!"

                if self.check_for_buffered_data():
                    if self.verbose:
                       print "Data buffered locally, uploading it to the central server since it is back online."
                    self.upload_buffered_data()
                    self.set_buffered_data(0)
                    if not self.localstorage:
                        self.clear_buffer_data()

        if self.upload_to_weather_underground:
            self.weatherunderground()

        if self.verbose:
            print "|-------------------------------------------|"
            print 'TimeStamp:   {0}'.format(self.sensor_values.timestamp)
            print 'CPU Temp:    {0:0.2f} C \ {1:0.2f} F'.format(float(self.get_cpu_temperature()), float( ( float(self.get_cpu_temperature()) * 1.8 ) +32) )
            print 'Humidity:    {0}%'.format(getattr(self.sensor_values, self.humidity_flag).humidity)
            print 'Temperature = {0:0.2f} C'.format(getattr(self.sensor_values, self.pressure_flag).temp[0])   # Print temperature in C
            print 'Temperature = {0:0.2f} F'.format(getattr(self.sensor_values, self.pressure_flag).temp[1])             # Print temperature in F
            print "\r\n"
            if self.bmp085_enabled:
                print '085 Pressure = {0:0.4f} Pa'.format(self.sensor_values.bmp085.pressure)   # Print pressure in pascal
                print '085 Pressure = {0:0.4f} mmhg'.format(self.sensor_values.bmp085.pressure / float(133.322368) )   # Print pressure in mm of Mercury
                print '085 Pressure = {0:0.4f} atm'.format(self.sensor_values.bmp085.pressure / float(101325) )    # Print pressure in Atmospheres
                print '085 Altitude = {0:0.4f} m'.format(self.sensor_values.bmp085.altitude)
                print "\r\n"
            if self.bmp180_enabled:
                print '180 Pressure = {0:0.4f} Pa'.format(self.sensor_values.bmp180.pressure)   # Print pressure in pascal
                print '180 Pressure = {0:0.4f} mmhg'.format(self.sensor_values.bmp180.pressure / float(133.322368) )   # Print pressure in mm of Mercury
                print '180 Pressure = {0:0.4f} atm'.format(self.sensor_values.bmp180.pressure / float(101325) )    # Print pressure in Atmospheres
                print '180 Altitude = {0:0.4f} m'.format(self.sensor_values.bmp180.altitude)
                print "\r\n"
            if self.bmp280_enabled:
                print '280 Pressure = {0:0.4f} Pa'.format(self.sensor_values.bmp280.pressure)   # Print pressure in pascal
                print '280 Pressure = {0:0.4f} mmhg'.format(self.sensor_values.bmp280.pressure / float(133.322368) )   # Print pressure in mm of Mercury
                print '280 Pressure = {0:0.4f} atm'.format(self.sensor_values.bmp280.pressure / float(101325) )    # Print pressure in Atmospheres
                print '280 Altitude = {0:0.4f} m'.format(self.sensor_values.bmp280.altitude)
                print "\r\n"

            print 'Photolevel = {0} '.format(self.sensor_values.photoresistor)    # Print photoresistor levels Higher number is lower light levels
            print ''
            print("-------------------------- Wind Speed --------------------------")
            print("Miles Per Hour: " + str(self.sensor_values.wind_speed[0]))
            print("Meters Per Second: " + str(self.sensor_values.wind_speed[1]))
            print("-------------------------- Wind Direction --------------------------")
            print("Cardinal Direction: " + str(self.sensor_values.wind_direction))
            print("--------------------------------------------------------------------")

            if len(self.sensor_values.fetch_error) > 0:
                print("-------------------------- Fetch Sensor Data Errors --------------------------")
                #i = 0
                #while i < len(self.sensor_values.fetch_error):
                print(self.sensor_values.fetch_error)
                print("----------------------------------------------------------------")
        self.sensor_values.fetch_error = []

        if self.debug:
            pprint(vars(self.sensor_values))

        if self.camera_enabled:
            if self.verbose:
                print "Start Picture capture."
            image = self.take_picture()
            img = Image.open( image)
            print image
            filename = os.path.basename(image)
            print filename
            draw = ImageDraw.Draw(img)
            #font = ImageFont.truetype(<font-file>, <font-size>)
            print self.text_font
            font = ImageFont.truetype(self.text_font, 40)
            print "after load of font"
            #draw.text((x, y),"Sample Text",(r,g,b))
            draw.text((10, 0), "Humidity:       " + str(self.sensor_values.dht11.humidity) + "% " ,self.text_color, font=font)
            draw.text((10, 60), "Temperature: " + str(self.sensor_values.dht11.temp[0]) + "C / " + str(self.sensor_values.dht11.temp[1]) + "F" ,self.text_color, font=font)
            draw.text((10, 930), str(datetime.datetime.now()) ,self.text_color, font=font)
            img.save(self.output_path + filename, quality=self.jpeg_quality)
            os.remove(image)
            print( "Saved Image: {0}".format(self.output_path + filename) )

        if self.localstorage or self.bufferlocally:
            self.update_station_timestamp()

        if self.verbose:
            print "|---------------------------------------------------------------------------|"

        return 1

    def set_buffered_data(self, flag):
        self.conn.executemany("UPDATE weather_data.Stations SET `buffered_data` = %s WHERE `station_hash` = %s ",
        [
            (flag, self.station_hash),
        ])
        self.db.commit()

    def update_station_timestamp(self):
        timestamp = str(datetime.datetime.utcnow())
        if self.debug:
            print "Update Station Timestamp "+timestamp+" : Station_Hash: " + self.station_hash
        self.conn.executemany("UPDATE weather_data.Stations SET `lastupdate` = %s WHERE station_hash = %s",
        [
            (timestamp, self.station_hash),
        ])
        self.db.commit()

    def upload_buffered_data(self):
        buffer = {}

        self.conn.executemany("SELECT dht11, dht22, bmp085, bmp180, bmp280, am2302, analog_temp_sensor, photoresistor, thermistor FROM weather_data.Station_sensors WHERE `station_hash` = %s", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()

        dht11_flag = data[0][0]
        dht22_flag = data[0][1]
        bmp085_flag = data[0][2]
        bmp180_flag = data[0][3]
        bmp280_flag = data[0][4]
        am2302_flag = data[0][5]
        analog_temp_sensor_flag = data[0][6]
        photoresistor_flag = data[0][7]
        thermistor_flag = data[0][8]


        count = 0
        if dht11_flag:
            count = self.count_dht11_buffers()
        print count

        if dht22_flag or count < 1:
            count = self.count_dht22_buffers()
        print count

        if bmp085_flag or count < 1:
            count = self.count_bmp085_buffers()
        print count

        if bmp180_flag or count < 1:
            count = self.count_bmp180_buffers()
        print count

        if bmp280_flag or count < 1:
            count = self.count_bmp280_buffers()
        print count

        if am2302_flag or count < 1:
            count = self.count_am2302_buffers()
        print count

        if analog_temp_sensor_flag or count < 1:
            count = self.count_analog_temp_sensor_buffers()
        print count

        if photoresistor_flag or count < 1:
            count = self.count_photoresistor_buffers()
        print count

        if thermistor_flag or count < 1:
            count = self.count_thermistor_buffers()
        print count


        if count < 1:
            if self.verbose:
                print "Count of buffered rows was 0."
            return 0
        if self.debug:
            print "Count for Buffered Data rows is: " + str(count)

        for n in range(0, count):
            buffer[n] = SensorValues.SensorValues()

        if self.debug:
            pprint(buffer)

        if dht11_flag:
            if self.debug:
                print "dht11"
            n = 0
            for row in self.get_dht11_buffers():
                buffer[n].dht11.humidity = row[0]
                buffer[n].timestamp = row[3]
                buffer[n].dht11.temp.append(row[1])
                buffer[n].dht11.temp.append(row[2])
                n = n + 1


        if dht22_flag:
            if self.debug:
                print "dht22"
            n = 0
            for row in self.get_dht22_buffers():
                buffer[n].dht22.humidity = row[0]
                buffer[n].dht22.temp.append(row[1])
                buffer[n].dht22.temp.append(row[2])
                n = n + 1

        if bmp085_flag:
            if self.debug:
                print "bmp085"
            n = 0
            for row in self.get_bmp085_buffers():
                buffer[n].bmp085.pressure = row[0]
                buffer[n].bmp085.temp.append(row[1])
                buffer[n].bmp085.temp.append(row[2])
                buffer[n].bmp085.altitude = row[3]
                n = n + 1

        if bmp180_flag:
            if self.debug:
                print "bmpp180"
            n = 0
            for row in self.get_bmp180_buffers():
                buffer[n].bmp180.pressure = row[0]
                buffer[n].bmp180.temp.append(row[1])
                buffer[n].bmp180.temp.append(row[2])
                buffer[n].bmp180.altitude = row[3]
                n = n + 1

        if bmp280_flag:
            if self.debug:
                print "bmp280"
            n = 0
            for row in self.get_bmp280_buffers():
                buffer[n].bmp280.pressure = row[0]
                buffer[n].bmp280.temp.append(row[1])
                buffer[n].bmp280.temp.append(row[2])
                buffer[n].bmp280.altitude = row[3]
                n = n + 1

        if am2302_flag:
            if self.debug:
                print "am2302"
            n = 0
            for row in self.get_am2302_buffers():
                buffer[n].am2302.humidity = row[0]
                buffer[n].am2302.temp.append(row[1])
                buffer[n].am2302.temp.append(row[2])
                n = n + 1

        if analog_temp_sensor_flag:
            if self.debug:
                print "ats"
            n = 0
            for row in self.get_analog_temp_sensor_buffers():
                buffer[n].analog_temp_sensor.append(row[0])
                buffer[n].analog_temp_sensor.append(row[1])
                n = n + 1

        if photoresistor_flag:
            if self.debug:
                print "photoresistor"
            n = 0
            for row in self.get_photoresistor_buffers():
                buffer[n].photoresistor = row[0]

        if thermistor_flag:
            if self.debug:
                print "thermistor"
            n = 0
            for row in self.get_thermistor_buffers():
                buffer[n].thermistor.append(row[0])
                buffer[n].thermistor.append(row[1])

        for row in buffer:
            pprint(buffer[row].bmp280.altitude)
            self.upload_data(buffer[row])

    def upload_data(self, buffered_values = None):
        if buffered_values is not None:
            if self.verbose:
                print "Uploading buffered data."
            self.sensor_values = buffered_values
        self.payload = Payload.PayloadData()
        self.payload.station_name = self.station_name
        self.payload.station_hash = self.station_hash
        self.payload.timestamp = str(self.sensor_values.timestamp)

        if self.debug:
            pprint(self.payload.timestamp)

        json_data = self.json_dump()

        if self.debug:
            pprint(json_data)

        url = self.PiWem_Central_Server + '/piwem/api/api.php'
        values = {'payload' : json_data, 'station_hash': self.station_hash, 'station_key': self.station_key, 'mode': 'importdata'}
        data = urllib.urlencode(values)
        fullurl = url + '?' + data
        if self.debug:
            pprint(data)
            print "FULL URL: " + fullurl
        try:
            response = urllib2.urlopen(fullurl)
            page = response.read()
            if self.debug:
                print "HTTP Response: "
                print page
            if response.getcode() == 200:
                if self.verbose:
                    print "Success!"
                return 1
            else:
                if self.verbose:
                    print "Error! " + str(response.getcode())
                return 0
        except urllib2.URLError, e:
            print e.reason, e.message, e.args
            return -1

    def clear_buffer_data(self):
        self.conn.executemany("DELETE FROM weather_data.am2302 WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.analog_temp_sensor WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.dht11 WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.dht22 WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.bmp085 WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.bmp180 WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.bmp280 WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.photoresistor WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.conn.executemany("DELETE FROM weather_data.thermistor WHERE `station_hash` = %s AND buffered_data = 1", [(self.station_hash),] )
        self.db.commit()

    def json_dump(self):
        if self.verbose:
            print "Start Dump."
        self.payload.station_data = {'bmp085':{}, 'bmp180':{}}
        if self.bmp085_enabled:
            if self.debug:
                print "bmp085"
                print self.sensor_values.bmp085.__dict__
            self.payload.station_data['bmp085'] = self.sensor_values.bmp085.__dict__

        if self.bmp180_enabled:
            if self.debug:
                print "bmp180"
                print self.sensor_values.bmp180.__dict__
            self.payload.station_data['bmp180'] = self.sensor_values.bmp180.__dict__

        if self.bmp280_enabled:
            if self.debug:
                print "bmp280"
                print self.sensor_values.bmp280.__dict__
            self.payload.station_data['bmp280'] = self.sensor_values.bmp280.__dict__

        if self.dht11_enabled:
            if self.debug:
                print "dht11"
                print self.sensor_values.dht11.__dict__
            self.payload.station_data['dht11'] = self.sensor_values.dht11.__dict__

        if self.dht22_enabled:
            if self.debug:
                print "dht22"
                print self.sensor_values.dht22.__dict__
            self.payload.station_data['dht22'] = self.sensor_values.dht22.__dict__

        if self.am2302_enabled:
            if self.debug:
                print "am2302"
                print self.sensor_values.am2302.__dict__
            self.payload.station_data['am2302'] = self.sensor_values.am2302.__dict__

        if self.photoresistor_enabled:
            if self.debug:
                print "photoresistor"
                print self.sensor_values.photoresistor
            self.payload.station_data['photoresistor'] = self.sensor_values.photoresistor

        if self.analog_temp_sensor_enabled:
            if self.debug:
                print "analog_temp_sensor"
                print self.sensor_values.analog_temp_sensor
            self.payload.station_data['ats'] = self.sensor_values.analog_temp_sensor

        if self.thermistor_enabled:
            if self.debug:
                print "thermistor"
                print self.sensor_values.thermistor
            self.payload.station_data['therm'] = self.sensor_values.thermistor

        if self.power_enabled:
            if self.debug:
                print "power"
                print self.sensor_values.power
            self.payload.station_data['power'] = self.sensor_values.power

        if self.verbose:
            print "Full Payload Dump";
        return json.dumps(self.payload.__dict__)

    def count_bmp085_buffers(self):
        self.conn.executemany("SELECT pressure, c_temp, f_temp, altitude FROM `weather_data`.`bmp085` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_bmp180_buffers(self):
        self.conn.executemany("SELECT pressure, c_temp, f_temp, altitude FROM `weather_data`.`bmp180` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_bmp280_buffers(self):
        self.conn.executemany("SELECT pressure, c_temp, f_temp, altitude FROM `weather_data`.`bmp280` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_dht11_buffers(self):
        self.conn.executemany("SELECT humidity, c_temp, f_temp FROM `weather_data`.`dht11` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        print len(data)
        return len(data)

    def count_dht22_buffers(self):
        self.conn.executemany("SELECT humidity, c_temp, f_temp FROM `weather_data`.`dht22` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_analog_temp_sensor_buffers(self):
        self.conn.executemany("SELECT c_temp, f_temp FROM `weather_data`.`analog_temp_sensor` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_photoresistor_buffers(self):
        self.conn.executemany("SELECT photolevel FROM `weather_data`.`photoresistor` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_am2302_buffers(self):
        self.conn.executemany("SELECT humidity, c_temp, f_temp FROM `weather_data`.`am2302` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def count_thermistor_buffers(self):
        self.conn.executemany("SELECT c_temp, f_temp FROM `weather_data`.`thermistor` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        data = self.conn.fetchall()
        return len(data)

    def get_bmp085_buffers(self):
        self.conn.executemany("SELECT pressure, c_temp, f_temp, altitude FROM `weather_data`.`bmp085` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_bmp180_buffers(self):
        self.conn.executemany("SELECT pressure, c_temp, f_temp, altitude FROM `weather_data`.`bmp180` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_bmp280_buffers(self):
        self.conn.executemany("SELECT pressure, c_temp, f_temp, altitude FROM `weather_data`.`bmp280` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_dht11_buffers(self):
        self.conn.executemany("SELECT humidity, c_temp, f_temp, `timestamp` FROM `weather_data`.`dht11` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_dht22_buffers(self):
        self.conn.executemany("SELECT humidity, c_temp, f_temp FROM `weather_data`.`dht22` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_analog_temp_sensor_buffers(self):
        self.conn.executemany("SELECT c_temp, f_temp FROM `weather_data`.`analog_temp_sensor` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_photoresistor_buffers(self):
        self.conn.executemany("SELECT photolevel FROM `weather_data`.`photoresistor` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_am2302_buffers(self):
        self.conn.executemany("SELECT humidity, c_temp, f_temp FROM `weather_data`.`am2302` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def get_thermistor_buffers(self):
        self.conn.executemany("SELECT c_temp, f_temp FROM `weather_data`.`thermistor` WHERE `station_hash` = %s AND buffered_data = 1 ORDER BY `timestamp` ASC", [(self.station_hash),] )
        # fetch all of the rows from the query
        return self.conn.fetchall()

    def getDegOfDirection(self, direction):
        if direction == "North":
            return 0
        elif direction == "North North East":
            return 22.5
        elif direction == "North East":
            return 45
        elif direction == "East North East":
            return 67.5
        elif direction == "East":
            return 90
        elif direction == "East South East":
            return 112.5
        elif direction == "South East":
            return 135
        elif direction == "South South East":
            return 157.5
        elif direction == "South":
            return 180
        elif direction == "South South West":
            return 202.5
        elif direction == "South West":
            return 225
        elif direction == "West South West":
            return 247.5
        elif direction == "West":
            return 270
        elif direction == "West North West":
            return 292.5
        elif direction == "North West":
            return 315
        elif direction == "North North West":
            return 337.5

    def weatherunderground(self):
        if self.verbose:
            print "Starting upload of Weather Underground Data to: " + self.wu_url

        if self.temp_flag == "bmp085":
            tempf = self.sensor_values.bmp085.temp[1]
        elif self.temp_flag == "bmp180":
            tempf = self.sensor_values.bmp180.temp[1]
        elif self.temp_flag == "bmp280":
            tempf = self.sensor_values.bmp280.temp[1]
        elif self.temp_flag == "am2302":
            tempf = self.sensor_values.am2302.temp[1]
        elif self.temp_flag == "dht11":
            tempf = self.sensor_values.dht11.temp[1]
        elif self.temp_flag == "dht22":
            tempf = self.sensor_values.dht22.temp[1]
        elif self.temp_flag == "ats":
            tempf = self.sensor_values.analog_temp_sensor[1]
        elif self.temp_flag == "therm":
            tempf = self.sensor_values.thermistor[1]

        if self.humidity_flag == "dht11":
            humidity_insert = self.sensor_values.dht11.humidity
        elif self.humidity_flag == "dht22":
            humidity_insert = self.sensor_values.dht22.humidity
        elif self.humidity_flag == "am2302":
            humidity_insert = self.sensor_values.am2302.humidity

        if self.pressure_flag == "bmp085":
            pressure_inch = (0.0002952998751 * self.sensor_values.bmp085.pressure)
        elif self.pressure_flag == "bmp180":
            pressure_inch = (0.0002952998751 * self.sensor_values.bmp180.pressure)
        elif self.pressure_flag == "bmp280":
            pressure_inch = (0.0002952998751 * self.sensor_values.bmp280.pressure)

        values = {
            'ID': self.wu_station_id,
            'PASSWORD': self.wu_station_key,
            'dateutc': self.sensor_values.timestamp,
            'softwaretype': 'RaspberryPi Weather Monitor (PiWeM)',
            'action': 'updateraw',
            'humidity': humidity_insert,
            'baromin': pressure_inch,
            'tempf': tempf,
            'winddir': self.getDegOfDirection(self.sensor_values.wind_direction),  #[0 - 360 instantaneous wind direction]
            'windspeedmph': self.sensor_values.wind_speed[0],  #[mph instantaneous wind speed]
            #'windgustmph' ,#[mph current wind gust, using software specific time period]
            #'windgustdir' ,#[0 - 360 using software specific time period]
            #'windspdmph_avg2m' ,#[mph 2 minute average wind speed mph]
            #'winddir_avg2m' ,#[0 - 360 2 minute average wind direction]
            #'windgustmph_10m' ,#[mph past 10 minutes wind gust mph]
            #'windgustdir_10m' ,#[0 - 360 past 10 minutes wind gust direction]
            'realtime': 1,
            #'rtfreq': 3
        }


        data = urllib.urlencode(values)
        fullurl = self.wu_url + '?' + data
        if self.debug:
            pprint(data)
            print "FULL URL: " + fullurl

        try:
            response = urllib2.urlopen(fullurl)
            page = response.read()
            if self.debug:
                print "HTTP Response: "
                print page
            if response.getcode() == 200:
                if self.verbose:
                    print "Success!"
                return 1
            else:
                if self.verbose:
                    print "Error! " + str(response.getcode())
                return 0
        except urllib2.URLError, e:
            print e.reason, e.message, e.args
            return -1
