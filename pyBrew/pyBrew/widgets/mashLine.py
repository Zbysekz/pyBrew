from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, \
    QGraphicsPixmapItem, QGraphicsScene
from PyQt6.QtGui import QPixmap
import datetime

class MashLine(QWidget):
    def __init__(self, temperature, time, gradient):
        super(MashLine, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./widgets/mashLine.ui', self)  # Load the .ui file
        # self.show() # Show the GUI

        self.edit_temp.setValue(temperature)
        self.edit_time.setValue(time)
        self.edit_gradient.setValue(gradient)

        self.update("not_reached")

    def update(self, state):
        #self.setColor("lime")
        pass

    def readValues(self):
        return self.edit_temp.value(), self.edit_time.value(), self.edit_gradient.value()

    def setColor(self, color):
        self.frame.setStyleSheet("background-color: " + color + ";")

    def setVersionColor(self, color):
        self.frame_2.setStyleSheet("background-color: " + color + ";")