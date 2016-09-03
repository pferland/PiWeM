import Adafruit_GPIO.I2C as I2C
import time

# Got the code for this at: https://forums.adafruit.com/viewtopic.php?f=19&t=89049
# Took the single running script and broke it down to a class

class bmp280:
    i2c = I2C
    device = None

    # this value is necessary to calculate the correct height above sealevel
    # its also included in airport weather information ATIS named as QNH
    # unit is hPa
    QNH=1020
    # power mode
    # POWER_MODE=0 # sleep mode
    # POWER_MODE=1 # forced mode
    # POWER_MODE=2 # forced mode
    POWER_MODE=3 # normal mode

    # temperature resolution
    # OSRS_T = 0 # skipped
    # OSRS_T = 1 # 16 Bit
    # OSRS_T = 2 # 17 Bit
    # OSRS_T = 3 # 18 Bit
    # OSRS_T = 4 # 19 Bit
    OSRS_T = 5 # 20 Bit

    # pressure resolution
    # OSRS_P = 0 # pressure measurement skipped
    # OSRS_P = 1 # 16 Bit ultra low power
    # OSRS_P = 2 # 17 Bit low power
    # OSRS_P = 3 # 18 Bit standard resolution
    # OSRS_P = 4 # 19 Bit high resolution
    OSRS_P = 5 # 20 Bit ultra high resolution

    # filter settings
    # FILTER = 0 #
    # FILTER = 1 #
    # FILTER = 2 #
    # FILTER = 3 #
    FILTER = 4 #
    # FILTER = 5 #
    # FILTER = 6 #
    # FILTER = 7 #

    # standby settings
    # T_SB = 0 # 000 0,5ms
    # T_SB = 1 # 001 62.5 ms
    # T_SB = 2 # 010 125 ms
    # T_SB = 3 # 011 250ms
    T_SB = 4 # 100 500ms
    # T_SB = 5 # 101 1000ms
    # T_SB = 6 # 110 2000ms
    # T_SB = 7 # 111 4000ms


    CONFIG = (T_SB <<5) + (FILTER <<2) # combine bits for config
    CTRL_MEAS = (OSRS_T <<5) + (OSRS_P <<2) + POWER_MODE # combine bits for ctrl_meas

    # print ("CONFIG:",CONFIG)
    # print ("CTRL_MEAS:",CTRL_MEAS)

    BMP280_REGISTER_DIG_T1 = 0x88
    BMP280_REGISTER_DIG_T2 = 0x8A
    BMP280_REGISTER_DIG_T3 = 0x8C
    BMP280_REGISTER_DIG_P1 = 0x8E
    BMP280_REGISTER_DIG_P2 = 0x90
    BMP280_REGISTER_DIG_P3 = 0x92
    BMP280_REGISTER_DIG_P4 = 0x94
    BMP280_REGISTER_DIG_P5 = 0x96
    BMP280_REGISTER_DIG_P6 = 0x98
    BMP280_REGISTER_DIG_P7 = 0x9A
    BMP280_REGISTER_DIG_P8 = 0x9C
    BMP280_REGISTER_DIG_P9 = 0x9E
    BMP280_REGISTER_CHIPID = 0xD0
    BMP280_REGISTER_VERSION = 0xD1
    BMP280_REGISTER_SOFTRESET = 0xE0
    BMP280_REGISTER_CONTROL = 0xF4
    BMP280_REGISTER_CONFIG  = 0xF5
    BMP280_REGISTER_STATUS = 0xF3
    BMP280_REGISTER_TEMPDATA_MSB = 0xFA
    BMP280_REGISTER_TEMPDATA_LSB = 0xFB
    BMP280_REGISTER_TEMPDATA_XLSB = 0xFC
    BMP280_REGISTER_PRESSDATA_MSB = 0xF7
    BMP280_REGISTER_PRESSDATA_LSB = 0xF8
    BMP280_REGISTER_PRESSDATA_XLSB = 0xF9

    def __init__(self, address = 0x76):
        self.device = self.i2c.get_i2c_device(address) # address of BMP
        if (self.device.readS8(self.BMP280_REGISTER_CHIPID) == 0x58): # check sensor id 0x58=BMP280
            self.device.write8(self.BMP280_REGISTER_SOFTRESET,0xB6) # reset sensor
            time.sleep(0.2) # little break
            self.device.write8(self.BMP280_REGISTER_CONTROL, self.CTRL_MEAS) #
            time.sleep(0.2) # little break
            self.device.write8(self.BMP280_REGISTER_CONFIG, self.CONFIG)  #
            time.sleep(0.2)
            # register_control = device.readU8(BMP280_REGISTER_CONTROL) # check the controll register again
            # register_config = device.readU8(BMP280_REGISTER_CONFIG)# check the controll register again
            # print("config:",register_config)
            # print("control:",register_control)

            self.dig_T1 = self.device.readU16LE(self.BMP280_REGISTER_DIG_T1) # read correction settings
            self.dig_T2 = self.device.readS16LE(self.BMP280_REGISTER_DIG_T2)
            self.dig_T3 = self.device.readS16LE(self.BMP280_REGISTER_DIG_T3)
            self.dig_P1 = self.device.readU16LE(self.BMP280_REGISTER_DIG_P1)
            self.dig_P2 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P2)
            self.dig_P3 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P3)
            self.dig_P4 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P4)
            self.dig_P5 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P5)
            self.dig_P6 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P6)
            self.dig_P7 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P7)
            self.dig_P8 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P8)
            self.dig_P9 = self.device.readS16LE(self.BMP280_REGISTER_DIG_P9)
        else:
            raise IOError("check sensor id 0x58=BMP280 failed, result was: " + str(self.BMP280_REGISTER_CHIPID))


    def read(self):
        raw_temp_msb=self.device.readU8(self.BMP280_REGISTER_TEMPDATA_MSB) # read raw temperature msb
        raw_temp_lsb=self.device.readU8(self.BMP280_REGISTER_TEMPDATA_LSB) # read raw temperature lsb
        raw_temp_xlsb=self.device.readU8(self.BMP280_REGISTER_TEMPDATA_XLSB) # read raw temperature xlsb
        raw_temp=(raw_temp_msb <<12)+(raw_temp_lsb<<4)+(raw_temp_xlsb>>4) # combine 3 bytes  msb 12 bits left, lsb 4 bits left, xlsb 4 bits right
        var1=(raw_temp/16384.0-self.dig_T1/1024.0)*self.dig_T2 # formula for temperature from datasheet
        var2=(raw_temp/131072.0-self.dig_T1/8192.0)*(raw_temp/131072.0-self.dig_T1/8192.0)*self.dig_T3 # formula for temperature from datasheet
        temp = (var1+var2)/5120.0 # formula for temperature from datasheet

        raw_press_msb=self.device.readU8(self.BMP280_REGISTER_PRESSDATA_MSB) # read raw pressure msb
        raw_press_lsb=self.device.readU8(self.BMP280_REGISTER_PRESSDATA_LSB) # read raw pressure lsb
        raw_press_xlsb=self.device.readU8(self.BMP280_REGISTER_PRESSDATA_XLSB) # read raw pressure xlsb
        raw_press=(raw_press_msb <<12)+(raw_press_lsb <<4)+(raw_press_xlsb >>4) # combine 3 bytes  msb 12 bits left, lsb 4 bits left, xlsb 4 bits right
        t_fine=(var1+var2) # need for pressure calculation
        var1=t_fine/2.0-64000.0 # formula for pressure from datasheet
        var2 = var1*var1*self.dig_P6/32768.0 # formula for pressure from datasheet
        var2 = var2+var1*self.dig_P5*2 # formula for pressure from datasheet
        var2 = var2/4.0+self.dig_P4*65536.0 # formula for pressure from datasheet
        var1=(self.dig_P3*var1*var1/524288.0+self.dig_P2*var1)/524288.0 # formula for pressure from datasheet
        var1=(1.0+var1/32768.0)*self.dig_P1 # formula for pressure from datasheet
        press=1048576.0-raw_press # formula for pressure from datasheet
        #print press
        press=(press-var2/4096.0)*6250.0/var1 # formula for pressure from datasheet
        #print press
        var1=self.dig_P9*press*press/2147483648.0 # formula for pressure from datasheet
        var2=press*self.dig_P8/32768.0 # formula for pressure from datasheet
        press = press +(var1+var2+self.dig_P7)/16.0 # formula for pressure from datasheet
        #print press
        altitude= 44330.0 * (1.0 - pow(press / (self.QNH*100), (1.0/5.255))) # formula for altitude from airpressure
        f_temp = ((temp * 9)/5)+32
        return ((temp, f_temp), press, altitude)


    def get_temp(self):
        data = self.read()
        return data[0]

    def get_pressure(self):
        data = self.read()
        return data[1]

    def get_altitude(self):
        data = self.read()
        return data[2]