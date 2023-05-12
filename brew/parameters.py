import platform
import configparser

class Parameters:
    config = configparser.ConfigParser()
    config.read('../config.ini')

    ON_RASPBERRY = platform.machine() != "x86_64"

    print(list(config.items()))
    NORMAL = 0
    RICH = 1
    FULL = 2
    verbosity = int(config['debug']['verbosity'])

    serialPort = config['general']['serialPort']
    server_ip_address = config['general']['server_ip_address']

    hlt_setpoint = float(config['processValues']['hlt_setpoint'])
    rvk_setpoint = float(config['processValues']['rvk_setpoint'])


    aut_setpoint0 = float(config['processValues']['aut_setpoint0'])
    aut_setpoint1 = float(config['processValues']['aut_setpoint1'])
    aut_setpoint2 = float(config['processValues']['aut_setpoint2'])
    aut_setpoint3 = float(config['processValues']['aut_setpoint3'])
    aut_setpoint4 = float(config['processValues']['aut_setpoint4'])

    aut_grad0 = float(config['processValues']['aut_grad0'])
    aut_grad1 = float(config['processValues']['aut_grad1'])
    aut_grad2 = float(config['processValues']['aut_grad2'])
    aut_grad3 = float(config['processValues']['aut_grad3'])
    aut_grad4 = float(config['processValues']['aut_grad4'])

    aut_time0 = float(config['processValues']['aut_time0'])
    aut_time1 = float(config['processValues']['aut_time1'])
    aut_time2 = float(config['processValues']['aut_time2'])
    aut_time3 = float(config['processValues']['aut_time3'])
    aut_time4 = float(config['processValues']['aut_time4'])

    persistentList = []

    @classmethod
    def Write(cls, dataContainer):
        for obj, key, prop in cls.persistentList:
            cls.config['processValues'][key] = str(dataContainer[key])

        with open('../config.ini', 'w') as configfile:
            cls.config.write(configfile)
    @classmethod
    def makePersistent(cls, object, key, prop): # and also load value from config
        cls.persistentList += [[object, str(key), str(prop)]]

        setattr(object[key], prop, float(cls.config['processValues'][key]))
