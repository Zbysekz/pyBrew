from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication
import sys
import logger
from forms.form_main import MainWindow
from logger import Log, LogException
from parameters import Parameters
import os
import pathlib
from subprocess import PIPE, Popen
import subprocess
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget,QMessageBox
from dataContainer import DataContainer
from arduinoComm import ArduinoComm
from driverComm import DriverComm
from stateMachine import StateMachine
from SQLserverComm import SQLcomm

rootPath = str(pathlib.Path(__file__).parent.absolute())
class cApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timerUpdateSW = QTimer()
        self.timerUpdateSW.timeout.connect(self.CheckForSWUpdate)
        self.parameters = Parameters()
        logger.setParameters(self.parameters)
        self.threads = {}  # track info about threads
        self.dataContainer = DataContainer()

        self.determineSerialPorts()

        self.arduinoComm = ArduinoComm(self.parameters, self.threads, self.dataContainer)
        self.driverComm = DriverComm(self.parameters, self.threads, self.dataContainer)
        self.stateMachine = StateMachine(self.dataContainer)

        self.SQLcomm = SQLcomm(self.parameters, self.dataContainer)

        self.mainWindow = MainWindow(self.parameters, self.dataContainer,
                                     self.arduinoComm, self.driverComm, self.stateMachine, self.SQLcomm)

        self.SQLcomm.SendDataToServer()  # then self-called

    def run(self):
        retCode = -1
        self.driverComm.process()  # then self-called
        try:
            self.mainWindow.update()
            self.mainWindow.show()

            self.timer.start(1000)
            self.timerUpdateSW.start(10000)

            retCode = self.app.exec()
        except Exception as e:
            LogException(e)

        self.arduinoComm.terminate=True
        self.driverComm.terminate=True
        self.SQLcomm.terminate=True
        Log("quitting")
        Log("Threads:" + str(self.threads.values()))
        for name, t in self.threads.items():
            if t is not None:
                print(f"{name} : " + str(t.is_alive()))
                t.cancel()
            else:
                print(f"This thread: {name} was not executed even once")
        sys.exit(retCode)

    def update(self):
        try:
            self.mainWindow.update()
            self.arduinoComm.process()
            self.stateMachine.process()
        except Exception as e:
            LogException(e)

    def showError(self, title, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def CheckForSWUpdate(self):
        updateFolder = rootPath+'/../update/'
        files = os.listdir(updateFolder)
        if len(files)>0:
            for f in files:
                os.replace(updateFolder+f, rootPath+"/"+os.path.basename(f)) # move to parent folder
                Log("------------------------------------ Updated new SW -----------------------")
                break

            os.popen('nohup /home/pi/brew/autorunMain.sh')
            self.mainWindow.close()

    def determineSerialPorts(self):
        Log("Trying to find devices..")

        # motor driver
        command = "source get_device.sh; getdevice 10c4:ea60"
        with  Popen(command, shell=True, executable="/bin/bash",stdout=PIPE, stderr=None) as process:
            output = process.communicate()[0].decode("utf-8")
            if "ttyUSB" in output:
                port =  "/dev/"+output.replace('\n',"")
                self.parameters.DRIVER_SERIALPORT = port
                Log(f"Found '{port}' for motor driver")
            else:
                Log(f"Error parsing arduino port! '{output}'")
        #arduino
        command = "source get_device.sh; getdevice 1a86:7523"
        with  Popen(command, shell=True, executable="/bin/bash", stdout=PIPE,
                    stderr=None) as process:
            output = process.communicate()[0].decode("utf-8")
            if "ttyUSB" in output:
                port = "/dev/"+output.replace('\n',"")
                self.parameters.SERIALPORT = port
                Log(f"Found '{port}' for arduino")
            else:
                Log(f"Error parsing arduino port! '{output}'")

if __name__ == '__main__':

    app = cApp()
    app.run()
