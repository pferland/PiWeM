

while True:
    GPIO.setup(27, GPIO.OUT)
    GPIO.output(27, False)
    GPIO.setup(27, GPIO.IN)
    count = 0
    print("GPIO Value: " + str(GPIO.input(27)))
    while not GPIO.input(27):
        count = count + 1
        time.sleep(0.05)

    print("---------------")
    print(count)

def discharge(a_pin, b_pin):
    global debug
    if debug:
        print str(datetime.datetime.utcnow().strftime('%S.%f')) + " Discharge Start"
    GPIO.setup(a_pin, GPIO.IN)
    GPIO.setup(b_pin, GPIO.OUT)
    GPIO.output(b_pin, False)
    time.sleep(0.005)
    if debug:
        print str(datetime.datetime.utcnow().strftime('%S.%f')) + " Discharge End"

def charge_time(a_pin, b_pin):
    global debug
    if debug:
        print str(datetime.datetime.utcnow().strftime('%S.%f')) + " Charge Time Start"
    GPIO.setup(a_pin, GPIO.IN)
    #GPIO.setup(a_pin, GPIO.OUT)
    count = 0
    GPIO.output(a_pin, True)
    while not GPIO.input(b_pin):
        count = count + 1
        time.sleep(0.0001)
    if debug:
        print str(datetime.datetime.utcnow().strftime('%S.%f')) + " Charge Time End"
    return count

def analog_read(a_pin, b_pin):
    global debug
    if debug:
        print str(datetime.datetime.utcnow().strftime('%S.%f')) + " Analog Read Start"
    discharge(a_pin)
    if debug:
        print str(datetime.datetime.utcnow().strftime('%S.%f')) + " Analog Read End"
    return charge_time(a_pin)

def getWindSpeedData(wind_speed_a_pin, wind_speed_b_pin):
    global debug, verbose
    total_runtime = 0.0
    prev_time = 0.0
    click = 0
    sample_length = 10.0
    prev_value = 0
    while total_runtime < sample_length:
        if verbose:
            sys.stdout.write(".")
        if debug:
            print "+++++++++++++++++++++++++++++++++++++++++++"
        start = time.time()
        read_value = analog_read(wind_speed_a_pin, wind_speed_b_pin)
        now = datetime.datetime.utcnow().strftime('%S.%f')
        calc = float( now ) - prev_time
        if debug:
            print( str( now ) + " : " + str( read_value ) )
            print "Difference in values: ( "+str(prev_value)+" - "+str(read_value)+" ) =  " + str(abs(prev_value - read_value))
        if ( abs(prev_value - read_value) > 10 ):
            prev_value = read_value
            click = click + 1
            if verbose:
                sys.stdout.write("+")
            if debug:
                print "*******************************************************************************************\r\n*******************************************************************************************\r\nCLICK!!!!!\r\n*******************************************************************************************\r\n*******************************************************************************************"
        sys.stdout.flush()
        end_process_time = time.time()
        prev_time = float( now )
        #if ( (read_value / 100) > 1 ) and ( calc > 0.02 ) and (read_value != prev_value) :
        time.sleep(0.05)
        end = time.time()
        calc_runtime = end - start
        total_runtime = total_runtime + calc_runtime
        if debug:
            print "Process run time: " + str(end_process_time - start)
            print "Time Difference:  " + str(calc)
            print str( now ) + " : " + str( read_value )
            print "Total Runtime: " + str( total_runtime )
            print "+++++++++++++++++++++++++++++++++++++++++++"

    rps = float( click / total_runtime ) / float(2)
    rpms = (rps * 60)
    meter_circumference = (float(7) / float(12)) * 3.14
    fpm = (meter_circumference * rpms)
    mph = float( fpm * 60 ) / 5280

    if debug:
        print "+++++-=-=-=-=-=-=-=-=+++++"
        print rps
        print rpms
        print meter_circumference
        print fpm
        print mph
        print "+++++-=-=-=-=-=-=-=-=+++++"

    if verbose:
        print str(sample_length) + " Seconds of runtime is up."
        print "There were " + str(click) + " Clicks detected. "
        print str(rps) + " Clicks a second average."
        print str(rpms) + " rpms"
        print "MPH: " + str( mph )


GPIO.setmode(GPIO.BCM)

while True:
    getWindSpeedData(19, 26)
    time.sleep(0.5)