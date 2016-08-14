from ConfigParser import ConfigParser
import os


class PiWeMConfig:
    def __init__(self):
        self.Config = ConfigParser()
        self.Config.read(os.path.join("./", "settings.ini"))


    def ConfigMap(self, section):
        dict1 = {section: {}}
        options = self.Config.options(section)
        for option in options:
            dict1[section][option] = self.Config.get(section, option)
        return dict1
