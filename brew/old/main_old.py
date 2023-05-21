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

        with open('../../config.ini', 'w') as configfile:  # save
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
