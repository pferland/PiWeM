import RPi.GPIO as GPIO
import picamera, os, MySQLdb, time, datetime

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from dht11 import dht11

class PIWEM:
    loop_int = 0
    take_picture_flag = 1
    verbose = 0
    pin = 0
    brightness = 0
    resolution = (0,0)
    jpeg_quality = 100
    text_font = ""
    text_color = (0,0,0)
    output_path = ""
    tmp_dir = ""
    db = None
    conn = None
    camera = None
    dht11_instance = None
    GPIO_obj = None


    def __init__(self, sql_host, sql_user, sql_password, pin, resolution, output_path, tmp_path, brightness = 50):
        self.db = MySQLdb.connect(host=sql_host, user=sql_user, passwd=sql_password)
        self.pin = pin
        self.camera = picamera.PiCamera()
        self.camera.brightness = brightness
        self.brightness = brightness
        self.camera.resolution = resolution
        self.output_path = output_path
        self.tmp_path = tmp_path
        self.loop_int = 0

        # initialize GPIO
        self.__GPIO_obj = GPIO
        self.__GPIO_obj.setwarnings(False)
        self.__GPIO_obj.setmode(GPIO.BCM)
        self.__GPIO_obj.cleanup()

        self.conn = self.db.cursor()

        # read data using pin 14
        self.dht11_instance = dht11.DHT11(pin=self.pin)


    def fetch_data(self):
        self.conn.execute("""SELECT id, humidity, f_temp, c_temp, time_stamp FROM data ORDER BY id DESC""")
        return self.conn.fetchone()


    def insert_data(self, data):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        self.conn.executemany("""INSERT INTO weather_data.data (humidity, f_temp, c_temp, time_stamp ) VALUES ( %s, %s, %s, %s) """,
        [
        (data[0], data[2], data[1], timestamp ),
        ])
        self.db.commit()


    def get_temp_humidity_data(self):
        result = self.dht11_instance.read()
        if result.is_valid():
            f_temp = ((int(result.temperature) * 9)/5)+32
            return result.humidity, result.temperature, f_temp
        return 0


    def get_berometer_data(self):

        return 0

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

        data = self.get_temp_humidity_data()
        if data:
            self.insert_data(data)
            if self.verbose:
                ts = time.time()
                timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

                print("TimeStamp: " + timestamp)
                print("Humidity:       " + str(data[0]) + "%")
                print("Temperature: " + str(data[1]) + "C / " + str(data[2]) + "F")

            if self.take_picture_flag:
                #draw.text((x, y),"Sample Text",(r,g,b))
                draw.text((10, 0), "Humidity:       " + str(data[0]) + "%" ,self.text_color, font=font)
                draw.text((10, 60), "Temperature: " + str(data[1]) + "C / " + str(data[2]) + "F" ,self.text_color, font=font)
                img.save(self.output_path + filename, quality=self.jpeg_quality)
                os.remove(image)
                print("Saved Image: " + self.output_path + filename)
            return 1
        else:
            print("Data return error.")
            return 0

