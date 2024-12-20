#!/usr/bin/python
import time, datetime
from INA219 import INA219
from INA3221 import INA3221
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
settings['analog_wind_vane_enabled'] = 0
settings['analog_wind_vane_channel'] = 0

mon = PiWeM.PIWEM( settings=settings)

use_ina3221 = 1
sleep = 5

if use_ina3221:
    ina = INA3221.INA3221()
    while 1:
        for i in range(1, 4, 1):
            if i == 1:
                continue
            timestamp = str(datetime.datetime.utcnow())

            ShuntVoltage_mV = ina.getShuntVoltage_mV(i)*-1
            Voltage_V       = ina.getBusVoltage_V(i)
            Current_mA      = ina.getCurrent_mA(i)*-1
            Power_mW        = Voltage_V * Current_mA


            print "------------------------------"
            print "Channel: " + str(i)
            print timestamp
            print "shunt:   %.2fmV\r\n" \
                  "bus:     %.2fV\r\n" \
                  "current: %dmA\r\n" \
                  "power:   %.2fmW" % ( ShuntVoltage_mV, Voltage_V, Current_mA, Power_mW )

            mon.conn.executemany("INSERT INTO weather_data.power_monitor ( station_hash, `channel`, `shunt_mV`, `voltage`, `current_mA`, `power_mW`, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s, %s) ",
            [
                (mon.station_hash, i, ShuntVoltage_mV, Voltage_V, Current_mA, Power_mW, timestamp),
            ])
            mon.db.commit()
        time.sleep(sleep)
else:
    ina = INA219.INA219(address=0x44)
    while 1:
        timestamp = str(datetime.datetime.utcnow())
        ShuntVoltage_mV = ina.getShuntVoltage_mV()*-1
        Voltage_V       = ina.getBusVoltage_V()
        Current_mA      = ina.getCurrent_mA()*-1
        Power_mW        = Voltage_V * Current_mA

        print "------------------------------"
        print timestamp
        print "shunt:   %.2fmV\r\n" \
              "bus:     %.2fV\r\n" \
              "current: %dmA\r\n" \
              "power:   %.2fmW" % ( ShuntVoltage_mV, Voltage_V, Current_mA, Power_mW )

        mon.conn.executemany("INSERT INTO weather_data.power_monitor ( station_hash, `shunt_mV`, `voltage`, `current_mA`, `power_mW`, `timestamp` ) VALUES ( %s, %s, %s, %s, %s, %s) ",
        [
            (mon.station_hash, ShuntVoltage_mV, Voltage_V, Current_mA, Power_mW, timestamp),
        ])
        mon.db.commit()
        time.sleep(sleep)
