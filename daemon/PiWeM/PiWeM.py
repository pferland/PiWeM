import RPi.GPIO as GPIO
import PCF8591 as ADC

import Adafruit_BMP.BMP085 as BMP085
import picamera, os, MySQLdb, time, datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from dht11 import dht11


class PIWEM:
    # Really just for the daemon to keep track of loop numbers during error loops, but its what number you want it to start counting at.
    loop_int = 0

    #Where you want the weather data to be logged to. so far just supports CSV and TSV
    sql_log_data = 1
    file_log = 0
    file_log_type = 'csv' # supports csv or tsv (comma or tab)

    # write values to the console
    verbose = 0

    #used to get much more data about what is happening, really only needed if you are fucking around with the code. Might get some nifty information ;-)
    dht_pin = 0

    # Flags to tell what sensor should get the temperature value, can only have one set at a time, if more tha ons set, than the last one that is run will overwrite the other.
    bmp = 0
    dht11_temp_flag = 0
    dht22_temp_flag = 0

    #Init values for the DHT sensors. Supports both the DHT11 and DHT22. Others will be added when I find and can buy other devices.
    dht11_instance = None
    dht22_instance = None

    # RasPi camera settings, defaults should work for both v1 and v2 of the camera
    take_picture_flag = 1
    camera = None
    brightness = 50
    resolution = (1920,1080)
    jpeg_quality = 100
    text_font = ""
    text_color = (255,0,0)
    output_path = ""
    tmp_dir = ""

    #Init values for the SQL connection only need the DB and conn, others are not needed to be static, can just grab them again from the settings var.
    db = None
    conn = None

    #PCF8591 Analog to Digital switcher init, address, and device settings, address up to 4 devices at once.
    pcf_instance = ADC
    pcf_address = 0x48
    photosresistor_channel = 0

    #BPM085 Barometer pressure sensor init and address
    bmp_instance = ADC
    bmp_address = 0x77

    #Init value for GPIO object
    GPIO_obj = None


    def __init__(self, sql_host='127.0.0.1', sql_user='piwem', sql_password='', dht11_pin=1, dht22_pin=2, pcf_address='0x48', bmp_address='0x77'):
        self.db = MySQLdb.connect(host=sql_host, user=sql_user, passwd=sql_password)
        self.dht11_pin = dht11_pin
        self.dht22_pin = dht22_pin
        self.bmp_address = bmp_address
        self.loop_int = 0

        # initialize GPIO
        self.GPIO_obj = GPIO
        self.GPIO_obj.setwarnings(False)
        self.GPIO_obj.setmode(GPIO.BCM)
        self.GPIO_obj.cleanup()
        self.pcf_instance.setup(pcf_address)
        self.bmp_instance.setup(bmp_address)
        self.conn = self.db.cursor()

        # read data using dht_pin 14
        if self.dht11_temp_flag:
            self.dht11_instance = dht11.DHT11(pin=self.dht11_pin)

        #if self.dht22_temp_flag:
        #    self.dht11_instance = dht22.DHT22(pin=self.dht22_pin)

        global sensor
        sensor = BMP085.BMP085()


    def enable_camera(self):
        self.camera = picamera.PiCamera()
        self.camera.brightness = self.brightness
        self.camera.resolution = self.resolution



    def fetch_data(self):
        self.conn.execute("SELECT id, humidity, f_temp, c_temp, time_stamp FROM data ORDER BY id DESC")
        return self.conn.fetchall()


    def insert_data(self, data):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        print data
        self.conn.executemany("INSERT INTO weather_data.data ( humidity, f_temp, c_temp, time_stamp ) VALUES ( %s, %s, %s, %s) ",
        [
        (data[2], data[0][1], data[0][0], timestamp ),
        ])
        self.db.commit()


    def get_humidity_data(self):
        result = self.dht11_instance.read()
        if result.is_valid():
            return result.humidity
        return 0


    def get_temp_data(self):
        if self.dht11_temp_flag:
            result = self.dht11_instance.read()
            if result.is_valid():
                f_temp = ((int(result.temperature) * 9)/5)+32
                return result.temperature, f_temp
#        elif self.dht22_temp_flag:
#            result = self.dht22_instance.read()
#            if result.is_valid():
#                f_temp = ((int(result.temperature) * 9)/5)+32
#                return result.temperature, f_temp
        elif self.bmp:
            temp = sensor.read_temperature()        # Read temperature to variable temp
            if temp is not 0:
                f_temp = ((int(temp) * 9)/5)+32
                return temp, f_temp
        return 0


    def get_barometer_data(self):
        pressure = sensor.read_pressure()       # Read pressure to variable pressure
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
        return self.pcf.read(self.photosresistor_channel)


    def take_picture(self):
        print("Take Picture.")
        image_name = self.tmp_dir + "Image_" + str(self.loop_int) + ".jpg"
        self.camera.capture(image_name)
        return image_name


    def get_data_trigger(self):
        if self.take_picture_flag:
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
                print 'Photolevel = {0:0.4f} '.format(data[2])    # Print photoresistor levels
                print ''
            if self.take_picture_flag:
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

