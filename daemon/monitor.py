from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM

import sys, time

PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings") #Open Settings.ini file and read contents

res_split = settings['resolution'].split(",") #Parse Resolution field and make it into a tuple
resolution = (int(res_split[0]),int(res_split[1]))

text_color_split = settings['text_color'].split(",") #Same for the Text color on the final image
text_color = (int(text_color_split[0]), int(text_color_split[1]), int(text_color_split[2]))

#create the main object and set a few extra settings aside from the defaults.
try:
    mon = PiWeM.PIWEM( sql_host=settings['sql_host'], sql_user=settings['sql_user'], sql_password=settings['sql_password'])
    mon.setup_dht11( dht11_pin=int(settings['dht11_pin']) )
    mon.setup_dht22( dht22_pin=int(settings['dht22_pin']) )

    mon.setup_bmp(address=settings['bmp_address']) # Don't think the BMP085 has a different address, but you can set it with the address variable
    mon.setup_pcf(address=settings['pcf_address']) # Default address for the PCF8591 is 0x48, so its hardcoded, but you can set it to what ever you want with the address variable

except IOError, e:
    print e.args
    print e.errno
    print e.filename
    print e.message
    print e.strerror
    sys.exit(1)

mon.verbose = 1
mon.take_picture_flag = 0
mon.photosresistor_channel = int( settings['photoresistor_channel'] )# Photoresistor on the PCF8591 channel 0
print mon.photosresistor_channel

#sensor to get the temp
mon.bmp_temp_flag = 1   # Barometer sensor to be used for temp
mon.dht11_temp_flag = 0 # DHT11 sensor to be used for temp
mon.dht22_temp_flag = 0 # DHT22 sensor to be used for temp

if mon.take_picture_flag: # if you have a camera and want to use it for taking pictures each loop, you can enable it with this flag.
    mon.enable_camera(brightness=int(mon.resolution), resolution=mon.resolution) #set the resolution and brightness while enabling it i guess you could do it afterwards, bit its not set to do that yet...

while 1: #lets start the main loop!!!!!!!!
    print("i = %d" % mon.loop_int) #What loop number are we at?

    try:
        get_data = mon.get_data_trigger()
        mon.loop_int = mon.loop_int + 1  #syntax parser says it can be shorter, but screw it, i want to know what its doing and its only what ~100k of text or am i too drunk to math?
        time.sleep(int(settings['sleep_time']))

    except IOError, e: # If Sensor Data return is a Failure, do not increment, and try again.
        print e.args
        print e.errno
        print e.filename
        print e.message
        print e.strerror
        print 'IOError, usually is that you have not set either the barometer (bcm085) or PCF8591 address correctly, or you were messing with the cables whole the daemon was running, or the hardware has failed. or something went wrong with the I2C bus... I mean come on....'
        time.sleep(5) # error sleep, it could just be that the humidity sensor or something didnt reset in time. which the dht11 is really bad at...
    except KeyboardInterrupt, e:
        if mon.take_picture_flag:
            mon.camera.close()
        print "Keyboard Interrupt detected, daemon/script closing."
        sys.exit(0)