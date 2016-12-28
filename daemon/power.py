#!/usr/bin/python
import time, MySQLdb, datetime
from INA219 import INA219
from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM

PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings") #Open settings.ini file and read contents

settings['localstorage'] = 1
settings['pcf8591_enabled'] = 0
settings['bmp085_enabled'] = 0
settings['bmp180_enabled'] = 0
settings['bmp280_enabled'] = 0
settings['dht11_enabled'] = 0
settings['dht22_enabled'] = 0
settings['am2302_enabled'] = 0
settings['thermistor_enabled'] = 0
settings['analog_temp_sensor_enabled'] = 0
settings['photoresistor_enabled'] = 0
settings['camera_enabled'] = 0
settings['analog_anemometer_enabled'] = 0
settings['analog_anemometer_channel'] = 3
settings['analog_wind_vane_enabled'] = 0
settings['analog_wind_vane_channel'] = 0

mon = PiWeM.PIWEM( settings=settings )

ina = INA219.INA219()

while 1:
    timestamp = str(datetime.datetime.utcnow())
    print "------------------------------"
    print timestamp
    print "shunt:   %.2fmV\r\n" \
          "bus:     %.2fV\r\n" \
          "current: %dmA\r\n" \
          "power:   %.2fmW" % ( ina.getShuntVoltage_mV()*-1, ina.getBusVoltage_V(), ina.getCurrent_mA()*-1, ina.getPower_mW()*-1 )

    mon.conn.executemany("INSERT INTO weather_data.power_monitor ( station_hash, `shunt_mV`, `voltage`, `current_mA`, `power_mW`, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
    [
        (mon.station_hash, ina.getShuntVoltage_mV()*-1, ina.getBusVoltage_V(), ina.getCurrent_mA()*-1, ina.getPower_mW()*-1, timestamp),
    ])
    mon.db.commit()
    time.sleep(1)