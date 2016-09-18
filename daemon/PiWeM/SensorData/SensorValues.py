import bmp085_data, bmp180_data, bmp280_data, dht11_data, dht22_data, am2302_data

class SensorValues(object):
    bmp085 = bmp085_data.bmp085_data()

    bmp180 = bmp180_data.bmp180_data()

    bmp280 = bmp280_data.bmp280_data()

    dht11 = dht11_data.dht11_data()

    dht22 = dht22_data.dht22_data()

    am2302 = am2302_data.am2302_data()

    thermistor          = []
    analog_temp_sensor  = []
    photoresistor       = 0

    fetch_error         = []
