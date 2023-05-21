from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, \
    QGraphicsPixmapItem, QGraphicsScene
from PyQt5.QtGui import QPixmap
import datetime
from PyQt5.QtCore import pyqtSignal

class MashLine(QWidget):
    def __init__(self, temperature, time, gradient, callback_change :pyqtSignal):
        super(MashLine, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./widgets/mashLine.ui', self)  # Load the .ui file
        # self.show() # Show the GUI

        self.edit_temp.setValue(temperature)
        self.edit_time.setValue(time)
        self.edit_gradient.setValue(gradient)

        self.edit_temp.valueChanged.connect(self.change)
        self.edit_time.valueChanged.connect(self.change)
        self.edit_gradient.valueChanged.connect(self.change)

        self.callback_change = callback_change

        self.update("not_reached")

    def change(self):
        self.callback_change.emit()

    def update(self, state):
        #self.setColor("lime")
        pass

    def readValues(self):
        return self.edit_temp.value(), self.edit_time.value(), self.edit_gradient.value()

    def setColor(self, color):
        self.frame.setStyleSheet("background-color: " + color + ";")

    def setVersionColor(self, color):
        self.frame_2.setStyleSheet("background-color: " + color + ";")