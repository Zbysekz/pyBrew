import platform
import configparser
import os
import pathlib

rootPath = str(pathlib.Path(__file__).parent.absolute())

print("imported")

class Parameters:
    NORMAL = 0
    RICH = 1
    FULL = 2

    def __init__(self):
        config = configparser.ConfigParser()
        configPath = os.path.join(rootPath, '../config.ini')
        cnt = len(config.read(configPath))

        if cnt == 0:
            raise RuntimeError("Cannot open config.ini file in working directory!")

        for p in config.items():
            for p2 in config[p[0]].items():

                setattr(self, p2[0].upper(), p2[1])

        #special conversion for verbosity
        if type(self.VERBOSITY) == str:
            self.VERBOSITY = int(config['debug']['verbosity'])

        if hasattr(self, "DEBUG_FLAG"):
            self.DEBUG_FLAG = eval(self.DEBUG_FLAG)
        if hasattr(self, "INSTANCE_CHECK"):
            self.INSTANCE_CHECK = eval(self.INSTANCE_CHECK)

    def save(self):
        config = configparser.ConfigParser()
        configPath = os.path.join(rootPath, '../config.ini')
        cnt = len(config.read(configPath))
        if cnt == 0:
            raise RuntimeError("Cannot open config.ini file in working directory!")

        for p in config.items():
            for p2 in config[p[0]].items():
                config.set(p[0], p2[0], str(getattr(self, p2[0].upper(), p2[1])))
        with open(os.path.join(rootPath, '../config.ini'), 'w') as configfile:
            config.write(configfile)


