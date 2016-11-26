import picamera, datetime

camera             = picamera.PiCamera()
camera.brightness  = 50
camera.resolution  = 3280,2464
camera.rotation    = 180
image_name = "/mnt/e/TimeLaps/frames/Image_" + str(datetime.datetime.utcnow()) + ".jpg"
camera.capture(image_name)

print image_name