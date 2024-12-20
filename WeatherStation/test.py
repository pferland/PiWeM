import RPi.GPIO as GPIO
import time, datetime, signal, time, sys
from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM
GPIO.setmode(GPIO.BCM)
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        GPIO.cleanup()
        sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

debug = 0
verbose = 1


PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings") #Open Settings.ini file and read contents

res_split = settings['resolution'].split(",") #Parse Resolution field and make it into a tuple
resolution = (int(res_split[0]), int(res_split[1]))

text_color_split = settings['text_color'].split(",") #Same for the Text color on the final image
text_color = (int(text_color_split[0]), int(text_color_split[1]), int(text_color_split[2]))

mon = PiWeM.PIWEM(settings=settings)
while 1:
    # time.sleep(1)
    print("|--------------------------------------------|")
    ret = mon.wind.getWindSpeedData()

    # mon.get_data_trigger()
    '''
    print("Photo Resistor: " + str(mon.sensor_values.photoresistor))
    print("Pressure: " + str(mon.sensor_values.bmp085.pressure))
    print("DHT22 Humidity: " + str(mon.sensor_values.dht11.humidity))
    print("DHT22 Temp: " + str(mon.sensor_values.dht11.temp))
    print("BMP180 Altitude: " + str(mon.sensor_values.bmp085.altitude))
    print("BMP180 Temperature: " + str(mon.sensor_values.bmp085.temp))
    print("-------------------------- Wind Speed --------------------------")
    print("Miles Per Hour: " + str(mon.sensor_values.wind_speed[0]))
    print("Meters Per Second: " + str(mon.sensor_values.wind_speed[1]))
    print("-------------------------- Wind Direction --------------------------")
    print("Cardinal Direction: " + str(mon.sensor_values.wind_direction))
    print("--------------------------------------------------------------------")
    '''
    print('CPU Temp:    {0:0.2f} C \ {1:0.2f} F'.format(float(mon.get_cpu_temperature()), float((float(mon.get_cpu_temperature()) * 1.8)+32)) +"\r\n\r\n" )
