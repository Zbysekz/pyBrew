import pygame
import sys
import os

from datetime import datetime
from screenManager import cScreenManager
from Logger import Log,LogException
from databaseMySQL import cMySQL

import threading
import configparser
import time
import serial
from parameters import Parameters
import pathlib

if Parameters.ON_RASPBERRY:
    import RPi.GPIO as GPIO
    import pigpio

import comm

# for periodicity mysql inserts
HOUR = 3600
MINUTE = 60

#14 reserve

stopOnThrow = True

MySQL = cMySQL()
MySQL_Thread = cMySQL()

rootPath = str(pathlib.Path(__file__).parent.absolute())

print(Parameters.server_ip_address)
class PygView(object):

    def __init__(self, width=1360, height=730, fps=30):
        """Initialize pygame, window, background, font,...
        """
        #window position
        # x = 10
        #y = 0
        #os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)

        if Parameters.ON_RASPBERRY:
            GPIO.setmode(GPIO.BCM)
            #GPIO.setup(Parameters.GPIO_OK_SIGNAL, GPIO.IN)#, pull_up_down=GPIO.PUD_UP) -- physical pull up is already fitted on this PIN

        self.signalStorageThreadLock = threading.Lock()
        self.signalStorage = []


        config = configparser.ConfigParser()
        config.read('../config.ini')
        #print(config['general']['path'])  # -> "/path/name/"
        fullscreen = config['general']['fullscreen'] == 'true'

        with open('../config.ini', 'w') as configfile:  # save
            config.write(configfile)


        pygame.init()
        pygame.display.set_caption("Brew")

        if fullscreen:
            # pygame.mouse.set_visible(False) - bugs the mouse event positions
            self.pyScreen = pygame.display.set_mode((0, 0), pygame.DOUBLEBUF | pygame.FULLSCREEN)
            self.pySurface = pygame.Surface(self.pyScreen.get_size()).convert()
            self.width, self.height = pygame.display.get_surface().get_size()

        else:
            self.width = width
            self.height = height

            self.pyScreen = pygame.display.set_mode((self.width, self.height), pygame.NOFRAME | pygame.DOUBLEBUF)
            self.pySurface = pygame.Surface(self.pyScreen.get_size()).convert()

        self.clock = pygame.time.Clock()
        self.fps = fps
        self.playtime = 0.0

        self.screenManager = cScreenManager(self.pyScreen)

        self.blinkTmr = 0
        self.blink = 0
        self.terminate = False
        self.blinkComm = False

        self.receiver = comm.Receiver()
        self.serialPortOpened = False

        # state machine
        self.screenManager.dataContainer['stateMachine_status'] = 0
        self.screenManager.dataContainer['stateMachine_on'] = False
        for i in range(5):
            self.screenManager.dataContainer['aut_remTime'+str(i)] = None
        self.screenManager.dataContainer['avg_grad'] = 0.0
        self.tmrMinuteCountdown = time.time()
        self.tmrAvgGrad = time.time()
        self.lastGradVal = 0.0
        self.threads = {}

        self.first_arduino_data_ready = False

    def run(self):
        """The mainloop
        """

        pygame.time.set_timer(pygame.USEREVENT + 1, 100)  # animate event
        pygame.time.set_timer(pygame.USEREVENT + 2, 500)  # update values event
        pygame.time.set_timer(pygame.USEREVENT + 3, 3000)  # communicate

        #self.GPIO_read() # for first time, then it is self-called
        self.SendDataToServer()
        self.CheckSerialPortOpened()
        self.HandleSerialPort()  # for first time, then it is self-called
        try:

            while not self.terminate:
                events = pygame.event.get()
                for event in events :
                    if event.type == pygame.QUIT:
                        self.terminate = True
                    elif event.type == pygame.USEREVENT + 1:
                        self.screenManager.animate()
                    elif event.type == pygame.USEREVENT + 2:
                        self.screenManager.updateValues()
                        self.ProcessIncomeData()
                    elif event.type == pygame.USEREVENT + 3:
                        #if self.CheckForSWUpdate():
                        #    self.terminate = True
                        if not self.serialPortOpened:
                            self.CheckSerialPortOpened()
                        self.SendDataToArduino()
                        self.RunStateMachine()
                        self.CalculateProcessValues()
                    else:
                        # keyboard and mouse events
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                Parameters.Write(self.screenManager.dataContainer)
                                self.terminate = True

                events = [e for e in events if e.type == pygame.KEYDOWN or e.type == pygame.MOUSEBUTTONDOWN]
                if len(events) > 0:
                    # feed every event into screenManager
                    self.screenManager.handleEvents(events)

                milliseconds = self.clock.tick(self.fps)
                self.playtime += milliseconds / 1000.0

                self.screenManager.draw()

                pygame.display.flip()
                self.pyScreen.blit(self.pySurface, (0, 0))

        except Exception as e:
            Log("Exception for main run()")
            LogException(e)

            if stopOnThrow:
                pygame.quit()
                #raise e

        self.terminate = True
        Log("pygame quit")
        Log("Threads:" + str(self.threads.values()))
        for name, t in self.threads.items():
            if t is not None:
                print(f"{name} : " + str(t.is_alive()))
                t.cancel()
            else:
                print(f"This thread: {name} was not executed even once")
        pygame.quit()

    def CheckSerialPortOpened(self):
        try:
            self.serialPort = serial.Serial( Parameters.serialPort, timeout=0.1)  # open serial port
            self.serialPortOpened = True
            Log("Serial port opened.")
        except Exception as e:
            Log("Serial port opening error! " + str(e))

    def HandleSerialPort(self):

        if self.serialPortOpened:
            done = False
            while not done and not self.terminate:
                try:
                    char = self.serialPort.read(1)
                except serial.serialutil.SerialException:
                    Log("Lost serial port!")
                    self.serialPortOpened = False
                    break
                if len(char) < 1 or char == b'':
                    done = True
                else:
                    self.receiver.Receive(char[0])


        if not self.terminate:
            tmr = threading.Timer(0.5, self.HandleSerialPort)  # calling itself periodically
            tmr.start()
            self.threads["serialPortThread"] = tmr
        else:
            if self.serialPortOpened:
                self.serialPort.close()


    def ProcessIncomeData(self):
        container = self.screenManager.dataContainer

        container['commFail'] = not self.serialPortOpened
        while True:  # process all data
            if self.serialPortOpened:
                data = comm.getRcvdData()
                #print("received:"+str(data))

                if len(data) > 0:
                    if data[0] == 1:
                        container['hlt_value'] = getVal(data, 1)
                        container['rvk_value'] = getVal(data, 3)
                        container['scz_value'] = getVal(data, 5)

                        container['errorFlags'] = (int)(getVal(data, 7)) + ((int)(getVal(data, 9)) << 16)
                        container['outputs'] = (int)(data[11])

                        self.first_arduino_data_ready = True
                else:
                    break
            else:
                container['hlt_value'] = 0
                container['rvk_value'] = 0
                container['scz_value'] = 0
                container['errorFlags'] = 0
                container['outputs'] = 0
                break



    def SendDataToArduino(self):

        bitsPacked = packBits(self.screenManager.dataContainer['hlt_on'], self.screenManager.dataContainer['hlt_PID'],
                              self.screenManager.dataContainer['rvk_on'], self.screenManager.dataContainer['rvk_PID'])
        #print("PACKED:")
        #print([i for i in bitsPacked])
        #print(int.from_bytes(bitsPacked[0],"little",signed=False))
        
        data = bytes([1]) + bitsPacked + getBytes(self.screenManager.dataContainer['hlt_setpoint']) +\
            getBytes(self.screenManager.dataContainer['rvk_setpoint'])

        pkg = comm.CreatePacket(data)
        #print(pkg)
        if self.serialPortOpened:
            self.serialPort.write(pkg)

    def CalculateProcessValues(self):

        PERIOD = 2  # min
        if time.time() - self.tmrAvgGrad > 60*PERIOD and self.first_arduino_data_ready:  # 2 MIN
            self.tmrAvgGrad = time.time()

            self.screenManager.dataContainer['avg_grad'] = (self.screenManager.dataContainer['rvk_value'] - self.lastGradVal) / PERIOD
            self.lastGradVal = self.screenManager.dataContainer['rvk_value']

    def RunStateMachine(self):
        data = self.screenManager.dataContainer
        status = data.get('stateMachine_status')
        if data.get('stateMachine_on'):

            if status >= 0 and status < 5:
                # dont do SP reached for temperatures above 90C
                if not data['sp_reached'] or data['aut_grad'+str(status)] >= 90:
                    data['rvk_setpoint'] = data['aut_grad'+str(status)]
                else:
                    data['rvk_setpoint'] = data['aut_grad' + str(status)]*0.2  # just standby power
                data['rvk_PID'] = False

                if data['rvk_value'] >= data['aut_setpoint'+ str(status)]:
                    data['rvk_on'] = False
                    data['sp_reached'] = True

                    if data['aut_remTime'+ str(status)] is None:  # start counting
                        data['aut_remTime'+ str(status)] = data['aut_time' + str(status)]
                else:
                    data['rvk_on'] = True

                if data['aut_remTime' + str(status)] == 0:  # time elapsed
                    data['sp_reached'] = False
                    data['stateMachine_status'] += 1


            if time.time() - self.tmrMinuteCountdown >= 60:
                self.tmrMinuteCountdown = time.time()
                for i in range(5):
                    if data['aut_remTime' + str(i)] is not None and data['aut_remTime' + str(i)] > 0:
                        data['aut_remTime' + str(i)] -= 1



    def SendDataToServer(self):
        global MySQL_Thread
        try:
            #print("Send data to server check")
            if self.first_arduino_data_ready and MySQL_Thread.PersistentConnect():
                data = self.screenManager.dataContainer
                #print("Sending")
                MySQL_Thread.insertValue("temperature", 'hlt_value', data['hlt_value'], periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                MySQL_Thread.insertValue("temperature", 'rvk_value', data['rvk_value'], periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                MySQL_Thread.insertValue("temperature", 'scz_value', data['scz_value'], periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                MySQL_Thread.insertValue("temperature", 'errorFlags', data['errorFlags'], periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                MySQL_Thread.insertValue("temperature", 'avg_grad', data['avg_grad'], periodicity=60 * MINUTE,
                                         writeNowDiff=0.3)
                MySQL_Thread.insertValue("temperature", 'hlt_setpoint', data['hlt_setpoint'], periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                MySQL_Thread.insertValue("temperature", 'rvk_setpoint', data['rvk_setpoint'], periodicity=60 * MINUTE,
                                         writeNowDiff=1)



                MySQL_Thread.PersistentDisconnect()
        except Exception as e:
            Log("Exception for main SendDataToServer()")
            LogException(e)

        if not self.terminate:
            tmr = threading.Timer(120, self.SendDataToServer)  # calling itself periodically
            tmr.start()
            self.threads["UpdateValuesFromServerThread"] = tmr

    def CheckForSWUpdate(self):
        updateFolder = rootPath+'/update/'
        files = os.listdir(updateFolder)
        if len(files)>0:
            for f in files:
                os.replace(updateFolder+f, rootPath+"/"+os.path.basename(f)) # move to parent folder
                Log("updated:"+str(f))

            os.popen('nohup /home/pi/brew/autorunMain.sh')
            return True
        return False

####

def getVal(data, idx):
    return (data[idx] * 256 + data[idx+1])/100.0

def getBytes(val):
    return bytes([int(round(val * 100) / 256), int(round(val * 100)) % 256])

def packBits(*bits):
    result = 0
    position = 0
    for b in bits:
        if b:
            result += (1 << position)
        position += 1
    return bytes([result & 0xFF, (result & 0xFF00) >> 8])


if __name__ == '__main__':
    # call with width of window and fps
    Log("Script started")
    if (len(sys.argv) > 1):
        if ('delayStart' in sys.argv[1]):
            Log("Delayed start...")
            time.sleep(20)
    PygView().run()
    if Parameters.ON_RASPBERRY:
        GPIO.cleanup()
