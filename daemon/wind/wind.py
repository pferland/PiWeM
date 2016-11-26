import RPi.GPIO as GPIO
import time, datetime, signal, sys


class wind:
    def __init__(self):
        self.positions = [1.0, 2.1, 3.8, 16.0, 120.0, 65.0, 33.0, 8.2]
        self.north_pos_index = 0
        GPIO.setmode(GPIO.BCM)

        self.wind_speed_a_pin = 19
        self.wind_speed_b_pin = 26

        self.wind_diretion_a_pin = 6
        self.wind_diretion_b_pin = 13

    def discharge(self, a_pin, b_pin):
        GPIO.setup(a_pin, GPIO.IN)
        GPIO.setup(b_pin, GPIO.OUT)
        GPIO.output(b_pin, False)
        time.sleep(0.005)

    def charge_time(self, a_pin, b_pin):
        GPIO.setup(b_pin, GPIO.IN)
        GPIO.setup(a_pin, GPIO.OUT)
        count = 0
        GPIO.output(a_pin, True)
        while not GPIO.input(b_pin):
            count = count + 1
        return count

    def analog_read(self, a_pin, b_pin):
        self.discharge(a_pin, b_pin)
        return self.charge_time(a_pin, b_pin)

    def getWindSpeedData(self):
        total_runtime = 0.0
        prev_time = 0.0
        click = 0
        sample_length = 260.0
        prev_value = 0
        while total_runtime < sample_length:
            print "+++++++++++++++++++++++++++++++++++++++++++"
            start = time.time()
            read_value = self.analog_read(self.wind_speed_a_pin, self.wind_speed_b_pin)
            now = datetime.datetime.utcnow().strftime('%S.%f')
            calc = float( now ) - prev_time
            print( str( now ) + " : " + str( read_value ) )
            print "Difference in values: ( "+str(prev_value)+" - "+str(read_value)+" ) =  " + str(abs(prev_value - read_value))
            if (prev_value - read_value) > 2000:
                prev_value = read_value
                click = click + 1
                print "*******************************************************************************************\r\n*******************************************************************************************\r\nCLICK!!!!!\r\n*******************************************************************************************\r\n*******************************************************************************************"
            end_process_time = time.time()
            prev_time = float( now )
            #if ( (read_value / 100) > 1 ) and ( calc > 0.02 ) and (read_value != prev_value) :
            time.sleep(0.05)
            end = time.time()
            calc_runtime = end - start
            total_runtime = total_runtime + calc_runtime

            print "Process run time: " + str(end_process_time - start)
            print "Time Difference:  " + str(calc)
            print str( now ) + " : " + str( read_value )
            print "Total Runtime: " + str( total_runtime )
            print "+++++++++++++++++++++++++++++++++++++++++++"

        GPIO.cleanup()
        meter_meters_width = 0.1778 * 3.14

        clicks_per_second = click / total_runtime
        rpms = clicks_per_second / 2

        print str(sample_length) + " Seconds of runtime is up."
        print "There were " + str(click) + " Clicks detected. "
        print str(clicks_per_second) + " Clicks a second average."
        print str(rpms) + " rpms"
        print "Maybe the m/s for the Anemometer: " + str( meter_meters_width * rpms ) + " ?"
        print "MPH: " + str( (meter_meters_width * rpms) * 2.237 ) + " - Absolute value: " + str(round( (meter_meters_width * rpms) * 2.237 ))
