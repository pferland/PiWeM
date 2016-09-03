import RPi.GPIO as GPIO
import PCF8591 as ADC
import Adafruit_BMP.BMP085 as BMP085
#import Adafruit_DHT.AM2302 as AM2302
import bmp280

#import Adafruit_BMP.BMP180 as BMP180 #Temp filler, till i get the hardware and can actually use it.
#import Adafruit_BMP.BMP280 as BMP280 #Temp filler, till i get the hardware and can actually use it.
import picamera, socket, sys, uuid, os, math, MySQLdb, time, datetime, SensorValues

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from dht11 import dht11

from pprint import pprint


global sensor

class PIWEM:
    # Really just for the daemon to keep track of loop numbers during error loops, but its what number you want it to start counting at.
    loop_int        = 0

    # This stations Hash, it should be generated on the first run and saved to the DB and the station_hash.txt file
    station_hash    = ""

    #Where you want the weather data to be logged to. so far just supports CSV and TSV Well not really, but it will be
    sql_log_data    = 1
    file_log        = 0
    file_log_type   = 'csv' # supports csv or tsv (comma or tab)

    # write values to the console
    verbose     = 1

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
    ds18b20_pin = 0


    #Init values for the DHT sensors. Supports both the DHT11 and DHT22. Others will be added when I find and can buy other devices.
    dht11_instance = None
    dht22_instance = None

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
    db = None
    conn = None

    #PCF8591 Analog to Digital switcher init, address, and device settings, address up to 4 devices at once.
    pcf8591_instance        = ADC
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

    #
    sensor_values = None

    def __init__(self, settings=[]):
        if not settings:
            raise ValueError("PiWeM settings argument was not set...")

        self.db = MySQLdb.connect(host=settings['sql_host'], user=settings['sql_user'], passwd=settings['sql_password'])
        self.conn = self.db.cursor()
        self.set_sensor_flags(settings)

        self.verbose = int(settings['verbose'])
        self.debug = int(settings['debug'])

        if not os.path.isfile("station_hash.txt"):
            station_hash_file   = open('station_hash.txt', 'w+')
            station_hash        = str(uuid.uuid4())
            station_hash_file.write(station_hash)
            station_hash_file.close()
            self.station_hash = station_hash

            self.insert_station_hash()
            self.insert_station_sensors()
        else:
            station_hash_file = open('station_hash.txt', 'r')
            self.station_hash = station_hash_file.read()
            station_hash_file.close()
            self.update_station_sensors()

        if self.debug:
            print "Station Hash: " + self.station_hash
        self.loop_int   = 0
        self.sleep_time = float(settings['sleep_time'])

        self.am2302_pin = settings['am2302_pin']
        self.dht11_pin   = settings['dht11_pin']
        self.dht22_pin   = settings['dht22_pin']
        self.ds18b20_pin = settings['ds18b20_pin']
        self.bmp085_address = int(settings['bmp085_address'], 16)
        self.bmp180_address = int(settings['bmp180_address'], 16)
        self.bmp280_address = int(settings['bmp280_address'], 16)
        self.pcf8591_address = int(settings['pcf8591_address'], 16)
        self.thermistor_channel = settings['thermistor_channel']
        self.ats_channel = settings['ats_channel']
        self.brightness = settings['brightness']
        self.resolution = settings['resolution']
        self.jpeg_quality = settings['jpeg_quality']
        self.photosresistor_channel = int( settings['photoresistor_channel'] )# Photoresistor on the PCF8591 channel 0
        self.ats_channel = int(settings['ats_channel'])
        self.thermistor_channel = int(settings['thermistor_channel'])

        # initialize GPIO
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        self.ATS_GPIO = GPIO
        self.ATS_GPIO.setup(27, GPIO.IN)

        self.sensor_values = SensorValues.SensorValues()
        self.setup_sensors()


    def set_sensor_flags(self, settings=[]):
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
        return 0


    def setup_sensors(self):
        self.setup_dht11( dht11_pin=int(self.dht11_pin) )
        self.setup_dht22( dht22_pin=int(self.dht22_pin) )
        self.setup_bmp085(address=self.bmp085_address) # Low (ground) on sda for the BMP is 0x76, High is 0x77
        #self.setup_bmp180(address=self.bmp180_address # Temp til I get a 180 to test with.)
        self.setup_bmp280(address=self.bmp280_address)
        self.setup_pcf8591(address=self.pcf8591_address) # Default address for the PCF8591 is 0x48, so its hardcoded, but you can set it to what ever you want with the address variable
        self.setup_am2302(self.am2302_pin)
        self.setup_camera()


    def insert_station_sensors(self):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

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
        self.conn.executemany("UPDATE weather_data.Station_sensors SET bmp085 = %s, bmp180 = %s, bmp280 = %s, dht11 = %s, dht22 = %s, thermistor = %s, analog_temp_sensor = %s, photoresistor = %s, camera = %s "
                              "WHERE station_hash = %s ",
        [
            (self.bmp085_enabled, self.bmp180_enabled, self.bmp280_enabled, self.dht11_enabled, self.dht22_enabled, self.thermistor_enabled, self.analog_temp_sensor_enabled, self.photoresistor_enabled, self.camera_enabled, self.station_hash),
        ])
        self.db.commit()
        return 0


    def insert_station_hash(self):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.conn.executemany("INSERT INTO weather_data.Stations ( station_hash, station_name, `timestamp` ) VALUES ( %s, %s, %s) ",
        [
            (self.station_hash, socket.gethostname(), timestamp),
        ])
        self.db.commit()
        return 0


    def setup_bmp085(self, address = 0x77):
        if self.bmp085_enabled:
            self.bmp085_address = address
            self.bmp085_instance = BMP085.BMP085(address=self.bmp085_address)
            return 0


    def setup_bmp180(self, address = 0x77):
        if self.bmp180_enabled:
            self.bmp180_address = address
            self.bmp180_instance = BMP085.BMP085(address=self.bmp180_address) #Temp filler, till i get the hardware and can actually use it.
            return 0


    def setup_bmp280(self, address = 0x76):
        if self.bmp280_enabled:
            self.bmp280_address = address
            self.bmp280_instance = bmp280.bmp280(address=self.bmp280_address) #Temp filler, till i get the hardware and can actually use it.
            return 0


    def setup_pcf8591(self, address = 0x48):
        if self.pcf8591_enabled:
            self.pcf8591_address = address
            self.pcf8591_instance.setup(self.pcf8591_address)
            return 0


    def setup_dht11(self, dht11_pin):
        if self.dht11_enabled:
            self.dht11_pin      = dht11_pin
            self.dht11_instance = dht11.DHT11(pin=self.dht11_pin)
            return 0


    def setup_dht22(self, dht22_pin):
        if self.dht22_enabled:
            self.dht22_pin = dht22_pin
            self.dht22_instance = dht11.DHT11(pin=self.dht22_pin)   # will add after the dht22 order comes in :/ ...
            return 0


    def setup_am2302(self, am2302_pin):
        if self.am2302_enabled:
            self.am2302_pin = am2302_pin
            self.am2302_instance = dht11.DHT11(pin=self.am2302_pin)   # will add after the dht22 order comes in :/ ...
            return 0


    def setup_camera(self):
        if self.camera_enabled:
            self.camera             = picamera.PiCamera()
            self.camera.brightness  = self.brightness
            self.camera.resolution  = self.resolution
            return 0


    def insert_data(self):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        if self.debug:
            print "--------- Insert Data values for self.sensor_values.*  ------------"
            print ""
            print "BMP085 Temp/Pressure"
            print self.sensor_values.bmp085_temp
            print self.sensor_values.bmp085_pressure

            print "BMP180 Temp/Pressure"
            print self.sensor_values.bmp180_temp
            print self.sensor_values.bmp180_pressure

            print "BMP280 Temp/Pressure"
            print self.sensor_values.bmp280_temp
            print self.sensor_values.bmp280_pressure

            print "DHT11 Temp/Humidty"
            print self.sensor_values.dht11_temp
            print self.sensor_values.dht11_humidity

            print "DHT22 Temp/Humidty"
            print self.sensor_values.dht22_temp
            print self.sensor_values.dht22_humidity

            print "Thermistor Temperature"
            print self.sensor_values.thermistor

            print "Analog Temperature Sensor"
            print self.sensor_values.analog_temp_sensor

            print "Photoresistor"
            print self.sensor_values.photoresistor

            print "Fetch Error Result Flag"
            if self.sensor_values.fetch_error:
                print self.sensor_values.fetch_error[0]
                print self.sensor_values.fetch_error[1]
            print "-------------------------------------------------------------------"

        if self.bmp085_enabled:
            if self.debug:
                print "bmp085_enabled"
            self.conn.executemany("INSERT INTO weather_data.bmp085 ( pressure, c_temp, f_temp, altitude, station_hash, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.bmp085_pressure, self.sensor_values.bmp085_temp[0], self.sensor_values.bmp085_temp[1], self.sensor_values.bmp085_altitude, self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.bmp180_enabled:
            if self.debug:
                print "bmp180_enabled"
            self.conn.executemany("INSERT INTO weather_data.bmp180 ( pressure, c_temp, f_temp, altitude, station_hash, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.bmp180_pressure, self.sensor_values.bmp180_temp[0], self.sensor_values.bmp180_temp[1], self.sensor_values.bmp180_altitude, self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.bmp280_enabled:
            if self.debug:
                print "bmp280_enabled"
                print self.sensor_values.bmp280_pressure
                print self.sensor_values.bmp280_temp
            self.conn.executemany("INSERT INTO weather_data.bmp280 ( pressure, c_temp, f_temp, altitude, station_hash, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.bmp280_pressure, self.sensor_values.bmp280_temp[0], self.sensor_values.bmp280_temp[1], self.sensor_values.bmp280_altitude, self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.dht11_enabled:
            if self.debug:
                print "dht11_enabled"
            self.conn.executemany("INSERT INTO weather_data.dht11 ( c_temp, f_temp, humidity, station_hash, `timestamp` ) VALUES ( %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.dht11_temp[0], self.sensor_values.dht11_temp[1], self.sensor_values.dht11_humidity, self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.dht22_enabled:
            if self.debug:
                print "dht22_enabled"
            self.conn.executemany("INSERT INTO weather_data.dht22 ( c_temp, f_temp, humidity, station_hash, `timestamp` ) VALUES ( %s, %s, %s, %s, %s) ",
            [
            (self.sensor_values.dht22_temp[0], self.sensor_values.dht22_temp[1], self.sensor_values.dht22_humidity, self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.thermistor_enabled:
            if self.debug:
                print "thermistor_enabled"
            self.conn.executemany("INSERT INTO weather_data.thermistor ( c_temp, f_temp, station_hash, `timestamp` ) VALUES (%s, %s, %s, %s) ",
            [
            (self.sensor_values.thermistor[0], self.sensor_values.thermistor[1], self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.analog_temp_sensor_enabled:
            if self.debug:
                print "analog_temp_sensor_enabled"
            self.conn.executemany("INSERT INTO weather_data.analog_temp_sensor ( c_temp, f_temp, station_hash, `timestamp` ) VALUES (%s, %s, %s, %s) ",
            [
            (self.sensor_values.ats_temp[0], self.sensor_values.ats_temp[1], self.station_hash, timestamp),
            ])
            self.db.commit()


        if self.photoresistor_enabled:
            if self.debug:
                print "photoresistor_enabled"
            self.conn.executemany("INSERT INTO weather_data.photoresistor ( `photolevel`, `station_hash`, `timestamp` ) VALUES ( %s, %s, %s) ",
            [
            (self.sensor_values.photoresistor, self.station_hash, timestamp),
            ])
            self.db.commit()
        return 0


    def get_am2302_data(self):
        if self.am2302_enabled:
            result = self.am2302_instance.read()
            f_temp = ((int(result.temperature) * 9)/5)+32

            if result.humidity is 0:
                print "Error fetching DHT Humidity"
                humidity_results = 0
            else:
                humidity_results = result.humidity
            if result.temperature is 0:
                temp_results = (0, 0)
                self.sensor_values.fetch_error = [1, "DHT11 fetch error"]
            else:
                temp_results = (result.temperature, f_temp)
            return temp_results, humidity_results*2
        return 0


    def get_dht11_data(self):
        if self.dht11_enabled:
            result = self.dht11_instance.read()
            f_temp = ((int(result.temperature) * 9)/5)+32

            if result.humidity is 0:
                print "Error fetching DHT Humidity"
                humidity_results = 0
            else:
                humidity_results = result.humidity
            if result.temperature is 0:
                temp_results = (0, 0)
                self.sensor_values.fetch_error = [1, "DHT11 fetch error"]
            else:
                temp_results = (result.temperature, f_temp)
            return temp_results, humidity_results*2
        return 0


    def get_bmp085_data(self):
        if self.bmp085_enabled:
            pressure = self.bmp085_instance.read_pressure()       # Read pressure to variable pressure
            if pressure is 0:
                self.sensor_values.fetch_error = [1, "BMP085 pressure fetch error"]
                raise IOError("Fetching Data Error BMP085 Pressure...")

            temp = self.bmp085_instance.read_temperature()        # Read temperature to variable temp
            if temp is 0:
                self.sensor_values.fetch_error = [1, "bmp085 temperature fetch error"]
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


    def get_thermistor_temp_data(self):   # Get Data from the Thermistor
        if self.thermistor_enabled:
            if self.debug:
                print "Thermistor Channel: "+ str(self.thermistor_channel)
            analogVal = self.pcf8591_instance.read(self.thermistor_channel)
            if self.debug:
                print "Analog Value for Thermistor: " + str(analogVal)
            if analogVal is 255:
                self.sensor_values.fetch_error = [1, "Thermistor result value error"]
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
                self.sensor_values.fetch_error = [1, "Analog Temperature Sensor value return error"]
                return 0, 0
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
            temp = temp - 273.15
            f_temp = ((int(temp) * 9)/5)+32
            tmp = self.ATS_GPIO.input(27)
            if self.debug:
                print "GPIO C temp: " + str(tmp) + "   Analog C Temp: " + str(temp) + "    Analog F Temp" + str(f_temp)
            #sys.exit(1)
            return temp, f_temp
        return 0


    def get_sensor_data(self):  # Gather all of the sensors data

        bmp085_data = self.get_bmp085_data()
        self.sensor_values.bmp085_temp = bmp085_data[0]
        self.sensor_values.bmp085_pressure = bmp085_data[1]
        self.sensor_values.bmp085_altitude = bmp085_data[2]

#        Future use, when I get the parts.
#        bmp180_data = self.get_bmp180_data()
#        self.sensor_values.bmp180_temp = bmp180_data[0]
#        self.sensor_values.bmp180_pressure = bmp180_data[1]

        bmp280_data = self.get_bmp280_data()
        self.sensor_values.bmp280_temp = bmp280_data[0]
        self.sensor_values.bmp280_pressure = bmp280_data[1]
        self.sensor_values.bmp280_altitude = bmp280_data[2]

        self.sensor_values.thermistor = self.get_thermistor_temp_data()

        self.sensor_values.ats_temp = self.get_ats_temp_data()

        dht11_data = self.get_dht11_data()
        self.sensor_values.dht11_temp = dht11_data[0]
        self.sensor_values.dht11_humidity = dht11_data[1]

        # Future Use, when I get the parts.
#        dht22_data = self.get_dht22_data()
#        self.sensor_values.dht22_temp = dht22_data[0]
#        self.sensor_values.dht22_humidity = dht22_data[1]

        self.sensor_values.photoresistor = self.get_photolevel_data()
        return 0


    def get_photolevel_data(self):  # Get levels from the Photoresistor
        print "photoresistor_enabled Value: " + str(self.photoresistor_enabled)
        if self.photoresistor_enabled:
            if self.debug:
                print "PhotoLevel: " + str(self.pcf8591_instance.read(self.photosresistor_channel))
            return self.pcf8591_instance.read(self.photosresistor_channel)
        return 0


    def take_picture(self):   # well i think this is self-explanatory...
        if self.debug:
            print("Take Picture.")
        image_name = self.tmp_dir + "Image_" + str(self.loop_int) + ".jpg"
        self.camera.capture(image_name)
        return image_name


    def get_data_trigger(self):  #Main loop trigger and handler for the daemon
        if self.camera_enabled:
            image = self.take_picture()
            img = Image.open( image)
            filename = os.path.basename(image)
            draw = ImageDraw.Draw(img)
            #font = ImageFont.truetype(<font-file>, <font-size>)
            font = ImageFont.truetype(self.text_font, 40)
        self.get_sensor_data()

#        if not self.sensor_values.fetch_error:
        self.insert_data()

        self.sensor_values.fetch_error = 0

        if self.verbose:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            print "|-------------------------------------------|"
            print 'TimeStamp:   {0}'.format(timestamp)
            print 'Humidity:    {0}%'.format(self.sensor_values.dht11_humidity)
            print 'Temperature = {0:0.2f} C'.format(self.sensor_values.dht11_temp[0])             # Print temperature in C
            print 'Temperature = {0:0.2f} F'.format(self.sensor_values.dht11_temp[1])             # Print temperature in F
            print "\r\n"
            print '085 Pressure = {0:0.4f} Pa'.format(self.sensor_values.bmp085_pressure)   # Print pressure in pascal
            print '085 Pressure = {0:0.4f} mmhg'.format(self.sensor_values.bmp085_pressure / float(133.322368) )   # Print pressure in mm of Mercury
            print '085 Pressure = {0:0.4f} atm'.format(self.sensor_values.bmp085_pressure / float(101325) )    # Print pressure in Atmospheres
            print '085 Altitude = {0:0.4f} m'.format(self.sensor_values.bmp085_altitude)
            print "\r\n"
            print '280 Pressure = {0:0.4f} Pa'.format(self.sensor_values.bmp280_pressure)   # Print pressure in pascal
            print '280 Pressure = {0:0.4f} mmhg'.format(self.sensor_values.bmp280_pressure / float(133.322368) )   # Print pressure in mm of Mercury
            print '280 Pressure = {0:0.4f} atm'.format(self.sensor_values.bmp280_pressure / float(101325) )    # Print pressure in Atmospheres
            print '280 Altitude = {0:0.4f} m'.format(self.sensor_values.bmp280_altitude)
            print "\r\n"
            print 'Photolevel = {0} '.format(self.sensor_values.photoresistor)    # Print photoresistor levels Higher number is lower light levels
            print ''
        if self.debug:
            pprint (vars(self.sensor_values))

        if self.camera_enabled:
            #draw.text((x, y),"Sample Text",(r,g,b))
            draw.text((10, 0), "Humidity:       " + str(self.sensor_values.dht11_humidity) + "% " ,self.text_color, font=font)
            draw.text((10, 60), "Temperature: " + str(self.sensor_values.bmp085_temp[0]) + "C / " + str(self.sensor_values.bmp085_temp[1]) + "F" ,self.text_color, font=font)
            img.save(self.output_path + filename, quality=self.jpeg_quality)
            os.remove(image)
            print( "Saved Image: {0}".format(self.output_path + filename) )
        return 1
 #       else:
 #           self.sensor_values.fetch_error = 0
 #           print("Data return error.")
 #           return 0

