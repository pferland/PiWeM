import RPi.GPIO as GPIO
import time, datetime, sys


class wind:

    def __init__(self, analog_wind_vane_pin=0, analog_wind_anemometer_pin=0, anemometer_sensor_diameter=0, debug=0, verbose=0):

        self.wind_direction_pin = analog_wind_vane_pin
        self.wind_speed_pin = analog_wind_anemometer_pin
        self.meter_diameter = anemometer_sensor_diameter
        self.circumference = (self.meter_diameter * 3.14)
        self.circumference_ft = self.circumference / 12
        self.debug = debug
        self.verbose = verbose
        self.cardinal = {
                0: 'North',
                10: 'North East',
                45: 'East',
                325: 'East South East',
                2700: 'South East',
                920: 'South',
                1400: 'South West',
                460: 'West',
                700: 'North West',
                145: 'North North West'
            }
        self.loops = 10

    def readDirection(self, RCpin):
        reading = 0
        GPIO.setup(RCpin, GPIO.OUT)
        GPIO.output(RCpin, False)
        GPIO.output(RCpin, GPIO.LOW)
        time.sleep(0.1)

        GPIO.setup(RCpin, GPIO.IN)
        # This takes about 1 millisecond per loop cycle
        while (GPIO.input(RCpin) == GPIO.LOW):
            reading += 1
        return reading

    def getDirection(self):
        I = 0
        buffer = 0
        while I < self.loops:
            buffer = buffer + self.readDirection(self.wind_direction_pin)
            I = I + 1

        average = buffer / self.loops
        rounded = round(average)
        Cardinal = self.getCardinal(rounded)
        if Cardinal == 0:
            return -1

        if self.debug:
            print("Average: " + str(average))
            print("Rounded: " + str(rounded))
            if Cardinal != 0:
                print("Cardinal: " + Cardinal)
            else:
                print("No Cardinal Found")
        return Cardinal


    def getCardinal(self, direction=0):
        if self.debug:
            print("Direction Number: " + str(direction))
        if direction == 0:
            return self.cardinal[direction]
        elif (direction < 20) and (direction > 5):
            return self.cardinal[10]
        elif (direction < 75) and (direction > 20):
            return self.cardinal[45]
        elif (direction < 375) and (direction > 250):
            return self.cardinal[325]
        elif (direction < 2900) and (direction > 2400):
            return self.cardinal[2700]
        elif (direction < 1700) and (direction > 1000):
            return self.cardinal[1400]
        elif (direction < 400) and (direction > 500):
            return self.cardinal[460]
        elif (direction < 800) and (direction > 650):
            return self.cardinal[700]
        elif (direction < 190) and (direction > 110):
            return self.cardinal[145]
        if self.debug:
            print("No Match")
        return 0

    def gpio_read(self, read_pin):
        GPIO.setup(read_pin, GPIO.OUT)
        GPIO.output(read_pin, False)
        GPIO.setup(read_pin, GPIO.IN)
        count = 0
        while not GPIO.input(read_pin):
            count = count + 1
            time.sleep(0.05)
        if self.debug:
            print("GPIO Value: " + str(GPIO.input(read_pin)))

        if self.debug:
            print("---------------")
            print(count)
        return count

    def getWindSpeedData(self):
        total_runtime = 0.0
        prev_time = 0.0
        click = 0
        sample_length = 15.0
        while total_runtime < sample_length:
            if self.debug:
                print "+++++++++++++++++++++++++++++++++++++++++++"
            start = time.time()
            read_value = self.gpio_read(self.wind_speed_pin)
            now = datetime.datetime.utcnow().strftime('%S.%f')
            #calc = float(now) - prev_time
            if read_value:
                click = click + 1
                sys.stdout.write(".")
                sys.stdout.flush()
                if self.debug:
                    print "*******************************************************************************************\r\n*******************************************************************************************\r\nCLICK!!!!!\r\n*******************************************************************************************\r\n*******************************************************************************************"
            #end_process_time = time.time()
            #prev_time = float(now)

            time.sleep(0.0001)

            end = time.time()
            calc_runtime = end - start
            total_runtime = total_runtime + calc_runtime

            #if self.debug:
                #print "Process run time: " + str(end_process_time - start)
                #print "Time Difference:  " + str(calc)
                #print str(now) + " : " + str(read_value)
        print "Total Runtime: " + str(total_runtime)
                #print "+++++++++++++++++++++++++++++++++++++++++++"

        ft_min = self.circumference_ft * ((click / 2) * 4)
        ft_hr = ft_min * 60
        milesPH = ft_hr / 5280
        metersPS = milesPH * 0.44704

        '''
        meter_meters_width = 

        clicks_per_second = (click / 2) / total_runtime
        rps = clicks_per_second / 2
        milesPH = (meter_meters_width * rps) * 2.237
        metersPS = meter_meters_width * rps
        '''
        sys.stdout.write("\r\n")
        sys.stdout.flush()
        if self.verbose:
            print("circumference: " + str(self.circumference))
            print("circumference_ft: " + str(self.circumference_ft))
            print str(sample_length) + " Seconds of runtime is up."
            print "There were " + str(click / 2) + " rotations detected. "
            print str( ((click / 2) * 4) / 60 ) + " rotations a second average."
            print str( ((click / 2) * 4)) + " rotations per minute"
            print "Maybe the m/s for the Anemometer: " + str(metersPS) + " ?"
            print "MPH: " + str(milesPH)

        return milesPH, metersPS