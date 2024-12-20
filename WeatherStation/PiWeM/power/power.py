from INA219 import INA219
from INA3221 import INA3221


class power:
    def __init__(self, sql_db, power_monitor, power_monitor_device, INA219_address, INA3221_address, debug, verbose):
        self.db = sql_db
        self.conn = self.db.cursor()
        self.power_monitor_device = power_monitor_device
        self.power_monitor = power_monitor
        self.debug = debug
        self.verbose = verbose
        self.INA219_address = INA219_address
        self.INA3221_address = INA3221_address

    def getpower(self):
        data_array = []
        if self.power_monitor_device == 'INA3221':
            ina = INA3221.INA3221(addr=self.INA3221_address)
            for i in range(1, 4, 1):
                if i == 1:
                    continue
                ShuntVoltage_mV = ina.getShuntVoltage_mV(i) * -1
                Voltage_V = ina.getBusVoltage_V(i)
                Current_mA = ina.getCurrent_mA(i) * -1
                Power_mW = Voltage_V * Current_mA

                if self.verbose:
                    print "------------------------------"
                    print "Channel: " + str(i)
                    print "shunt:   %.2fmV\r\n" \
                          "bus:     %.2fV\r\n" \
                          "current: %dmA\r\n" \
                          "power:   %.2fmW" % (ShuntVoltage_mV, Voltage_V, Current_mA, Power_mW)
                data_array.append((i, Current_mA, Power_mW, ShuntVoltage_mV, Voltage_V))
        else:
            ina = INA219.INA219(address=self.INA219_address)
            ShuntVoltage_mV = ina.getShuntVoltage_mV() * -1
            Voltage_V = ina.getBusVoltage_V()
            Current_mA = ina.getCurrent_mA() * -1
            Power_mW = Voltage_V * Current_mA
            if self.verbose:
                print "------------------------------"
                print "shunt:   %.2fmV\r\n" \
                      "bus:     %.2fV\r\n" \
                      "current: %dmA\r\n" \
                      "power:   %.2fmW" % (ShuntVoltage_mV, Voltage_V, Current_mA, Power_mW)
            data_array.append((0, Current_mA, Power_mW, ShuntVoltage_mV, Voltage_V))

        return data_array
