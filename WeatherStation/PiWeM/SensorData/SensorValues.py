from . import bmp085_data
from . import bmp180_data
from . import bmp280_data
from . import dht11_data
from . import dht22_data
from . import am2302_data


class UploadData:
    def __init__(self):
        self.temp = 0.0
        self.ftemp = 0.0
        self.humidity = 0.0
        self.pressure = 0.0

class SensorValues:
    def __init__(self):
        self.bmp085 = None
        self.bmp180 = None
        self.bmp280 = None
        self.dht11 = None
        self.dht22 = None
        self.am2302 = None
        self.upload_values = UploadData()
        self.timestamp = None
        self.upload_values.temp = None

        self.upload_values.temp = 0.0
        self.upload_values.humidity = 0.0
        self.upload_values.pressure = 0.0

        # Define each sensor's object
        self.bmp085 = bmp085_data.bmp085_data()
        self.bmp180 = bmp180_data.bmp180_data()
        self.bmp280 = bmp280_data.bmp280_data()
        self.dht11 = dht11_data.dht11_data()
        self.dht22 = dht22_data.dht22_data()
        self.am2302 = am2302_data.am2302_data()


        self.thermistor = [0.0, 0.0]
        self.analog_temp_sensor = [0.0, 0.0]
        self.photoresistor = 0.0

        self.wind_speed = [0.0, 0.0]
        self.wind_direction = ""

        self.fetch_error = []
