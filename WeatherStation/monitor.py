from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM
import sys
import time
import argparse

# Setup Argument Parser
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser(prog='Rasperry Pi Weather Monitor (PiWeM) ')
parser.add_argument('--version', action='version', version='%(prog)s 1.0')

parser.add_argument("--daemon", help="Run as a Daemon", action='store_true')
parser.add_argument("-d", help="Run as a Daemon", action='store_true')

parser.add_argument("--verbose", help="Run Verbosely", action='store_true')
parser.add_argument("-v", help="Run Verbosely", action='store_true')

parser.add_argument("--debug", help="Run Debug Mode", action='store_true')
parser.add_argument("-b", help="Run Debug Mode", action='store_true')

args = parser.parse_args()

# Load PiWeM Config values
PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings")  # Open settings.ini file and read contents

resolution = tuple(settings['resolution'].split(","))  # Parse Resolution field and make it into a tuple

text_color = tuple(settings['text_color'].split(",")) # Same for the Text color on the final image

# Create the main object and set a few extra settings aside from the defaults.
try:
    mon = PiWeM.PIWEM(settings=settings)

except IOError as e:
    print(e.args)
    print(e.errno)
    print(e.strerror)
    print(e.filename)
    print(e.message)
    sys.exit(1)

except ValueError as e:
    print(e.args)
    print(e.errno)
    print(e.strerror)
    print(e.filename)
    print(e.message)
    sys.exit(1)

try:
    if args['genhash']:
        if args['f']:
            print(mon.genhash())
        else:
            print(mon.get_station_hash())
except:
    print("No need to generate a new hash..")

# Lets start!
while 1:
    if mon.debug:
        print("i = %d" % mon.loop_int) # What loop number are we at?

    try:
        get_data = mon.get_data_trigger()
        mon.loop_int = mon.loop_int + 1

        if (args.daemon is not None) & (args.d is not None):
            print("Sleeping for " + str(mon.sleep_time) + " Seconds.")
            time.sleep(mon.sleep_time)
        else:
            sys.exit(0)

    except IOError as e:  # If Sensor Data return is a Failure, do not increment, and exit. there is an error....
        print(e.args)
        print(e.errno)
        print(e.filename)
        print(e.message)
        print(e.strerror)
        print('IOError, usually is that you have not set either the barometer (bcm085) or PCF8591 address correctly, '
              'or you were messing with the cables while the daemon was running, or the hardware has failed. '
              'or something went wrong with the I2C bus... I mean come on....')
        sys.exit(0)

    except KeyboardInterrupt as e:
        if mon.camera_enabled:
            mon.camera.close()
        print("Keyboard Interrupt detected, daemon/script closing.")
        sys.exit(0)
        
    except ValueError as e:
        print(e.args)
        print(e.message)
        sys.exit(0)
