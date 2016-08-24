import RPi.GPIO as GPIO
import PCF8591 as ADC

import Adafruit_BMP.BMP085 as BMP085
#import Adafruit_BMP.BMP180 as BMP180 #Temp filler, till i get the hardware and can actually use it.
#import Adafruit_BMP.BMP280 as BMP280 #Temp filler, till i get the hardware and can actually use it.
import picamera, sys, os, math, MySQLdb, time, datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from dht11 import dht11

sensor = None
global sensor

class PIWEM:
    # Really just for the daemon to keep track of loop numbers during error loops, but its what number you want it to start counting at.
    loop_int = 0

    #Where you want the weather data to be logged to. so far just supports CSV and TSV Well not really, but it will be
    sql_log_data    = 1
    file_log        = 0
    file_log_type   = 'csv' # supports csv or tsv (comma or tab)

    # write values to the console
    verbose = 0

    #used to get much more data about what is happening, really only needed if you are fucking around with the code. Might get some nifty information ;-)
    debug = 0

    #Enable or disables devices.
    pcf_enabled = 0
    bmp085_enabled = 0
    bmp180_enabled = 0
    bmp280_enabled = 0
    dht11_enabled = 0
    dht22_enabled = 0
    thermistor_enabled = 0
    analog_temp_sensor_enabled = 0
    photoresistor_enabled = 0
    camera_enabled      = 0

    # GPIO Pins for devices
    dht11_pin = 0
    dht22_pin = 0
    ds18b20_pin = 0

    # Flags to tell what sensor should get the temperature value, can only have one set at a time, if more tha ons set, than the last one that is run will overwrite the other.
    # ats (analog temp sensor), ds18b20, therm, bmp085, bmp180, bmp280
    temp_flag   = "dht11"

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
    pcf8591_instance            = ADC
    pcf8591_address             = -1
    photosresistor_channel  = -1
    ats_channel             = -1
    thermistor_channel      = -1


    #BPM085 Barometer pressure sensor init and address
    bmp085_instance    = None
    bmp085_address     = -1


    #BPM180 Barometer pressure sensor init and address
    bmp180_instance    = None
    bmp180_address     = -1


    #BPM280 Barometer pressure sensor init and address
    bmp280_instance    = None
    bmp280_address     = -1

    def __init__(self, settings=[]):
        if not settings:
            raise ValueError("PiWeM settings argument was not set...")

        self.db = MySQLdb.connect(host=settings['sql_host'], user=settings['sql_user'], passwd=settings['sql_password'])
        self.loop_int   = 0
        # initialize GPIO

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.cleanup()
        self.ATS_GPIO = GPIO
        self.ATS_GPIO.setup(27, GPIO.IN)

        self.conn = self.db.cursor()


    def setup_bmp085(self, address = '0x77'):
        hex_int = int(address, 16)
        self.bmp085_enabled = 1
        self.bmp085_address = hex_int
        self.bmp085_instance = BMP085.BMP085()


    def setup_bmp180(self, address = '0x77'):
        hex_int = int(address, 16)
        self.bmp180_enabled = 1
        self.bmp180_address = hex_int
#        self.bmp085_instance = BMP180.BMP180() #Temp filler, till i get the hardware and can actually use it.


    def setup_bmp280(self, address = '0x77'):
        hex_int = int(address, 16)
        self.bmp280_enabled = 1
        self.bmp280_address = hex_int
#        self.bmp085_instance = BMP280.BMP280() #Temp filler, till i get the hardware and can actually use it.


    def setup_pcf8591(self, address = '0x48'):
        hex_int = int(address, 16)
        self.pcf8591_address = hex_int
        self.pcf8591_instance.setup(self.pcf8591_address)
        self.pcf_enabled = 1


    def setup_dht11(self, dht11_pin):
        self.dht11_pin      = dht11_pin
        self.dht11_instance = dht11.DHT11(pin=self.dht11_pin)
        self.dht11_enabled = 1


    def setup_dht22(self, dht22_pin):
        self.dht22_pin = dht22_pin
        #self.dht22_instance = dht22.DHT22(pin=self.dht22_pin)   # will add after the dht22 order comes in :/ ...
        self.dht22_enabled = 1


    def setup_camera(self):
        if self.camera_enabled:
            self.camera             = picamera.PiCamera()
            self.camera.brightness  = self.brightness
            self.camera.resolution  = self.resolution
            self.camera_enabled     = 1


    def fetch_data(self):
        self.conn.execute("SELECT id, humidity, f_temp, c_temp, time_stamp FROM data ORDER BY id DESC")
        return self.conn.fetchall()


    def insert_data(self, data):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print data
        self.conn.executemany("INSERT INTO weather_data.data ( humidity, f_temp, c_temp, pressure, photolevel, time_stamp ) VALUES ( %s, %s, %s, %s, %s, %s) ",
        [
        (data[2], data[0][1], data[0][0], data[1], data[3], timestamp),
        ])
        self.db.commit()

    #def insert_


    def get_humidity_data(self):
        result = self.dht11_instance.read()
        if result.is_valid():
            return result.humidity
        return 0


    def get_temp_data(self):
        if self.temp_flag is "dht11":
            result = self.dht11_instance.read()
            if result.is_valid():
                f_temp = ((int(result.temperature) * 9)/5)+32
                return result.temperature, f_temp
#        elif self.temp_flag is "dht22":
#            result = self.dht22_instance.read()
#            if result.is_valid():
#                f_temp = ((int(result.temperature) * 9)/5)+32
#                return result.temperature, f_temp
        elif self.temp_flag is "bmp085":
            temp = sensor.read_temperature()        # Read temperature to variable temp
            if temp is not 0:
                f_temp = ((int(temp) * 9)/5)+32
                return temp, f_temp
        elif self.temp_flag is "ats":
            analogVal = self.pcf8591_instance.read(self.ats_channel)
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
            temp = temp - 273.15
            f_temp = ((int(temp) * 9)/5)+32
            tmp = self.ATS_GPIO.input(27)
            print tmp, temp, f_temp
            sys.exit(1)
            return temp, f_temp
        elif self.temp_flag is "therm":
            print self.thermistor_channel
            analogVal = self.pcf8591_instance.read(self.thermistor_channel)
            Vr = 5 * float(analogVal) / 255
            Rt = 10000 * Vr / (5 - Vr)
            temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
            temp = temp - 273.15
            f_temp = ((int(temp) * 9)/5)+32
            print temp, f_temp
            sys.exit(1)
            return temp, f_temp



        return 0


    def get_barometer_data(self):
        pressure = self.bmp085_instance.read_pressure()       # Read pressure to variable pressure
        if pressure is not 0:
            return pressure
        else:
            return 0


    def get_sensor_data(self):
        temp = self.get_temp_data()
        pressure = self.get_barometer_data()
        humidity = self.get_humidity_data()
        photolevel = self.get_photolevel_data()
        return temp, pressure, humidity, photolevel


    def get_photolevel_data(self):
        print "PhotoLevel: " + str(self.pcf8591_instance.read(0))
        return self.pcf8591_instance.read(self.photosresistor_channel)


    def take_picture(self):
        print("Take Picture.")
        image_name = self.tmp_dir + "Image_" + str(self.loop_int) + ".jpg"
        self.camera.capture(image_name)
        return image_name


    def get_data_trigger(self):
        if self.camera_enabled:
            image = self.take_picture()
            img = Image.open( image)
            filename = os.path.basename(image)
            draw = ImageDraw.Draw(img)
            #font = ImageFont.truetype(<font-file>, <font-size>)
            font = ImageFont.truetype(self.text_font, 40)

        data = self.get_sensor_data()

        if data:
            self.insert_data(data)
            if self.verbose:
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                print "|-------------------------------------------|"
                print 'TimeStamp:   {0}'.format(timestamp)
                print 'Humidity:    {0}%'.format(data[2]*2)
                print 'Temperature = {0:0.2f} C'.format(data[0][0])             # Print temperature in C
                print 'Temperature = {0:0.2f} F'.format(data[0][1])             # Print temperature in F
                print 'Pressure = {0:0.4f} Pa'.format(data[1])   # Print pressure in pascal
                print 'Pressure = {0:0.4f} mmhg'.format(data[1] / float(133.322368) )   # Print pressure in mm of Mercury
                print 'Pressure = {0:0.4f} atm'.format(data[1] / float(101325) )    # Print pressure in Atmospheres
                print 'Photolevel = {0} '.format(data[3])    # Print photoresistor levels
                print ''
            if self.camera_enabled:
                #draw.text((x, y),"Sample Text",(r,g,b))
                draw.text((10, 0), "Humidity:       " + str(data[0]) + "% " ,self.text_color, font=font)
                draw.text((10, 60), "Temperature: " + str(data[1]) + "C / " + str(data[2]) + "F" ,self.text_color, font=font)
                img.save(self.output_path + filename, quality=self.jpeg_quality)
                os.remove(image)
                print( "Saved Image: {0}".format(self.output_path + filename) )
            return 1
        else:
            print("Data return error.")
            return 0

