from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication
import sys
import logger
from forms.form_main import MainWindow
from logger import Log, LogException
from parameters import Parameters
import os
import threading
import subprocess
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget,QMessageBox
from dataContainer import DataContainer

class cApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.parameters = Parameters()
        logger.setParameters(self.parameters)

        self.dataContainer = DataContainer()
        self.mainWindow = MainWindow(self.parameters, self.dataContainer)

    def run(self):
        try:
            self.mainWindow.update()
            self.mainWindow.show()

            self.timer.start(4000)

            retCode = self.app.exec()
            sys.exit(retCode)
        except Exception as e:
            LogException(e)

    def update(self):
        pass

    def showError(self, title, text):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(text)
        msg.setWindowTitle(title)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

if __name__ == '__main__':

    app = cApp()
    app.run()
