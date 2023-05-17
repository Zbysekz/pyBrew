import json

from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QStackedWidget, QMessageBox, QFileDialog, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtCore import pyqtSignal, QObject
from logger import Log
from widgets.mashLine import MashLine

class Communicate(QObject):

    closeApp = pyqtSignal()
    showNotFoundError = pyqtSignal()


class MainWindow(QMainWindow):
    def __init__(self, parameters, dataContainer):
        super(MainWindow, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./forms/form_main.ui', self)  # Load the .ui file
        self.parameters = parameters
        self.setWindowTitle("PyBrew app")
        self.dataContainer = dataContainer
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
        self.btnAdd.clicked.connect(self.addMashLine)
        self.btnRemove.clicked.connect(self.removeMashLine)
        self.actionLoad.triggered.connect(self.load_recipe_from_file)
        self.actionSave.triggered.connect(self.save_recipe_to_file)

        self.menuTest.addAction("Nazdar")
        self.menuTest.addAction("Bazar")
        self.menuTest.addAction("Hurá")

        for i in ["COM1", "Bazar", "Hurá"]:
            self.menuTest.addAction(i)


        self.btnFan.mousePressEvent = self.toggleFan  # because this btn is actually label
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.timer.start(1000)

        self.statusbar.addWidget(QLabel("No recipe loaded"))

        self.show_status_dialog = False
        self.logged_user_name = None
        self.logged_user_personal_num = None
        self.show()

        self.mashLines = []

        self.recipe = {}

        if len(self.parameters.LAST_OPEN_PATH) > 0:
            self.load_recipe_from_file(withoutDialog=True)
            self.build_recipe(self.recipe)

        self.fan_state = False
        
    def toggleFan(self, *arg, **kwargs):
        self.dataContainer.fan_state = not self.dataContainer.fan_state
        if self.dataContainer.fan_state:
            self.btnFan.setStyleSheet("background-color: rgb(85, 255, 0);")
        else:
            self.btnFan.setStyleSheet("")

    def addMashLine(self):
        if len(self.recipe.keys()) > 0:
            maxKey = max([int(i) for i in self.recipe.keys()])
        else:
            maxKey = 0
        maxKey += 1
        self.recipe[str(maxKey)] = [66.0, 10, 1.0]
        self.retrieve_recipe()
        self.build_recipe(self.recipe)

    def removeMashLine(self):
        if len(self.recipe.keys()) > 0:
            del self.recipe[str(max([int(i) for i in self.recipe.keys()]))]
            self.build_recipe(self.recipe)

    def build_recipe(self, recipe):
        layout = self.grp_mash.layout()
        for l in self.mashLines:
            layout.removeWidget(l)
        self.mashLines.clear()
        for line in recipe.values():
            wd = MashLine(*line)
        # wd.setFixedHeight(60)
            self.mashLines.append(wd)
            layout.addWidget(wd)

    def load_recipe_from_file(self, withoutDialog=False):
        if not withoutDialog:
            fname = QFileDialog.getOpenFileName(
                self,
                "Open File",
                self.parameters.LAST_OPEN_PATH,
                "All Files (*);; Python Files (*.rcp);;",
            )
            filename = fname[0]
        else:
            filename = self.parameters.LAST_OPEN_PATH

        if len(filename)>0:
            try:
                f = open(filename, 'r')
                with f:
                    data = f.read()
                    self.recipe = json.loads(data)
                    self.build_recipe(self.recipe)

                    self.statusbar.findChild(QLabel).setText(f"Načten recept {filename}")
                    self.statusbar.showMessage("Načteno!", 2000)

                    self.parameters.LAST_OPEN_PATH = filename
                    self.parameters.save()
            except Exception as e:
                self.showError(f"Nezdařilo se načíst recept! {repr(e)}")

    def retrieve_recipe(self):
        ptr = 1
        for l in self.mashLines:
            temp, time, gradient = l.readValues()
            self.recipe[str(ptr)] = [temp, time, gradient]
            ptr += 1

    def save_recipe_to_file(self):

        self.retrieve_recipe()

        fileName, _ = QFileDialog.getSaveFileName(self, "QFileDialog.getSaveFileName()", "",
                                                  "All Files (*);;Text Files (*.rcp)")
        if fileName:
            try:
                f = open(fileName, 'w')
                with f:
                    f.write(json.dumps(self.recipe))

            except Exception as e:
                self.showError(f"Nezdařilo se uložit recept! {repr(e)}")

    def show_status(self):
        self.show_status_dialog = True

    def showError(self, str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(str)
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event):  # overriden method from ui
        self.close()

    def show_settings(self):
        self.form_settings.show()

    def show_about(self):
        self.form_about.show()

    def keyPressEvent(self, event):
        #if event.key() == Qt.Key.Key_Escape:
        pass

    def update(self):
        if self.show_status_dialog:
            self.form_status = FormStatus(self.db, self.parameters, self.logged_user_name)
            self.form_status.show()
            self.show_status_dialog = False
