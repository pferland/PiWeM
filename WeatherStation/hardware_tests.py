import argparse
from pprint import pprint

from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM

parser = argparse.ArgumentParser(prog='Rasperry Pi Weather Monitor (PiWeM) Unit Tests ')
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

mon = PiWeM.PiWeM(settings=settings)
mon.setup_dht11(pin=int(mon.dht11_pin))
#mon.setup_dht22(pin=int(mon.dht22_pin))
#mon.setup_am2302(pin=int(mon.am2302_pin))
#mon.setup_bmp085(address=mon.bmp085_address)  #  Low (ground) on sda for the BMP is 0x76, High is 0x77
mon.setup_bmp180(address=mon.bmp180_address)  #  Temp til I get a 180 to test with.
#mon.setup_bmp280(address=mon.bmp280_address)
#mon.setup_pcf8591(address=mon.pcf8591_address)  # Default address for the PCF8591 is 0x48, so its hardcoded, but you can set it to whatever you want with the address variable

mon.get_sensor_data()

pprint(mon.sensor_values.bmp180.pressure)
pprint(mon.sensor_values.bmp180.altitude)
pprint(mon.sensor_values.bmp180.temperature)
pprint(mon.sensor_values.bmp180.raw_temp)
pprint(mon.sensor_values.bmp180.raw_pressure)
pprint(mon.sensor_values.bmp180.sealevel_pressure)

pprint(mon.sensor_values.dht11.temperature)
pprint(mon.sensor_values.dht11.humidity)
