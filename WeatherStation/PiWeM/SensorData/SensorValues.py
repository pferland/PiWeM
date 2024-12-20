import bmp085_data, bmp180_data, bmp280_data, dht11_data, dht22_data, am2302_data, power_data


class SensorValues(object):
    def __init__(self):
        self.bmp085 = bmp085_data.bmp085_data()

        self.bmp180 = bmp180_data.bmp180_data()

        self.bmp280 = bmp280_data.bmp280_data()

        self.dht11 = dht11_data.dht11_data()

        self.dht22 = dht22_data.dht22_data()

        self.am2302 = am2302_data.am2302_data()

        self.power = [power_data.power_data(), power_data.power_data(), power_data.power_data()]

        self.thermistor = []
        self.analog_temp_sensor = []
        self.photoresistor = 0

        self.wind_speed = []
        self.wind_direction = ""

        self.timestsamp = ""
        self.fetch_error = []
