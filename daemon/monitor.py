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
    mon = PiWeM.PIWEM( settings=settings )

except IOError, e:
    print e.args
    print e.errno
    print e.strerror
    print e.filename
    print e.message
    sys.exit(1)
except ValueError, e:
    print e.args
    print e.errno
    print e.strerror
    print e.filename
    print e.message
    sys.exit(1)

while 1: #lets start the main loop!!!!!!!!
    if mon.debug:
        print("i = %d" % mon.loop_int) #What loop number are we at?

    try:
        get_data = mon.get_data_trigger()
        mon.update_station_timestamp()
        mon.loop_int = mon.loop_int + 1  #syntax parser says it can be shorter, but screw it, i want to know what its doing and its only what ~100k of text or am i too drunk to math?
        time.sleep(mon.sleep_time) #int(settings['sleep_time']))

    except IOError, e: # If Sensor Data return is a Failure, do not increment, and try again.
        print e.args
        print e.errno
        print e.filename
        print e.message
        print e.strerror
        print 'IOError, usually is that you have not set either the barometer (bcm085) or PCF8591 address correctly, or you were messing with the cables whole the daemon was running, or the hardware has failed. or something went wrong with the I2C bus... I mean come on....'
        time.sleep(mon.sleep_time) # error sleep, it could just be that the humidity sensor or something didnt reset in time. which the dht11 is really bad at...
    except KeyboardInterrupt, e:
        if mon.camera_enabled:
            mon.camera.close()
        print "Keyboard Interrupt detected, daemon/script closing."
        sys.exit(0)
    except ValueError, e:
        print e.args
        print e.errno
        print e.strerror
        print e.filename
        print e.message
        sys.exit(1)