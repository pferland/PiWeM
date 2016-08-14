from PiWeMConfig.PiWeMConfig import PiWeMConfig
from PiWeM import PiWeM
import sys, time

PWMConfig = PiWeMConfig()
settings = PWMConfig.ConfigMap("settings").get("settings")

res_split = settings['resolution'].split(",")
resolution = (int(res_split[0]),int(res_split[1]))

text_color_split = settings['text_color'].split(",")
text_color = (int(text_color_split[0]), int(text_color_split[1]), int(text_color_split[2]))

mon = PiWeM.PIWEM(settings['sql_host'], settings['sql_user'], settings['sql_password'], int(settings['temp_humidity_pin']), resolution, settings['output_path'], settings['tmp_dir'], brightness=int(settings['brightness']))
mon.jpeg_quality = int(settings['jpeg_quality'])
mon.text_font = settings['text_font']
mon.text_color = text_color
mon.verbose = 1
mon.take_picture_flag = 0

i = 0
while 1:
    print("i = %d" % i)
    mon.loop_int = i
    if mon.get_data_trigger():  # If Sensor Data return is a Failure, do not increment, and try again.
        time.sleep(int(settings['sleep_time']))
        i = i + 1
    else:
        time.sleep(5)
