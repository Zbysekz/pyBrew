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
    recipeChanged = pyqtSignal()


class MainWindow(QMainWindow):
    def __init__(self, parameters, dataContainer, arduinoComm, driverComm, stateMachine):
        super(MainWindow, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('./forms/form_main.ui', self)  # Load the .ui file
        self.parameters = parameters
        self.arduinoComm = arduinoComm
        self.driverComm = driverComm
        self.stateMachine = stateMachine


        self.setWindowTitle("PyBrew app")
        self.dataContainer = dataContainer
        self.c = Communicate()
        self.c.closeApp.connect(self.close)
        self.btnAdd.clicked.connect(self.addMashLine)
        self.btnRemove.clicked.connect(self.removeMashLine)
        self.actionLoad.triggered.connect(self.load_recipe_from_file)
        self.actionSave.triggered.connect(self.save_recipe_to_file)
        self.chk_HLT_pid.stateChanged.connect(self.hlt_pid_changed)
        self.chk_RVK_pid.stateChanged.connect(self.rvk_pid_changed)
        self.chk_RVK_on.stateChanged.connect(self.rvk_on_changed)
        self.chk_HLT_on.stateChanged.connect(self.hlt_on_changed)
        self.e_rvk_sp.valueChanged.connect(self.rvk_sp_changed)
        self.e_hlt_sp.valueChanged.connect(self.hlt_sp_changed)
        self.btnSkip.clicked.connect(self.stateMachine.skipStep)
        self.chk_stateMachine_on.stateChanged.connect(self.chk_state_machine_on_changed)
        self.btnSensorON.clicked.connect(self.sensorsON)
        self.btnSensorOFF.clicked.connect(self.sensorsOFF)

        #driver
        self.btnStirOnOff.clicked.connect(self.driverComm.CmdTurnOn)
        self.btnDriverReset.clicked.connect(self.driverComm.CmdReset)
        self.eDriver_sp.valueChanged.connect(self.driver_sp_changed)

        self.c.recipeChanged.connect(self.retrieve_recipe)

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

    def driver_sp_changed(self):
        self.dataContainer.driver_sp = self.eDriver_sp.value()
        self.driverComm.CmdSPChanged()

    def sensorsON(self):
        self.arduinoComm.set_sensorsON()

    def sensorsOFF(self):
        self.arduinoComm.set_sensorsOFF()

# TODO improve these both dir events
    def hlt_sp_changed(self):
        self.dataContainer.hlt_setpoint = self.e_hlt_sp.value()
    def rvk_sp_changed(self):
        self.dataContainer.rvk_setpoint = self.e_rvk_sp.value()
    def chk_state_machine_on_changed(self):
        if self.chk_stateMachine_on.isChecked():
            self.stateMachine.start()
    def hlt_pid_changed(self):
        self.dataContainer.hlt_PID = self.chk_HLT_pid.isChecked()

    def rvk_pid_changed(self):
        self.dataContainer.rvk_PID = self.chk_RVK_pid.isChecked()

    def hlt_on_changed(self):
        self.dataContainer.hlt_on = self.chk_HLT_on.isChecked()

    def rvk_on_changed(self):
        self.dataContainer.rvk_on = self.chk_RVK_on.isChecked()

    def toggleFan(self, *arg, **kwargs):
        self.dataContainer.fan_state = not self.dataContainer.fan_state
        self.update()

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
            wd = MashLine(*line, self.c.recipeChanged)
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
                    self.retrieve_recipe()

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
        self.dataContainer.recipe = self.recipe

        print("recipe retrieved")

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
                return False
            self.parameters.LAST_OPEN_PATH = fileName
            return True
        return False

    def showError(self, str):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(str)
        msg.setWindowTitle("Chyba")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def closeEvent(self, event):  # overriden method from ui
        self.close()


    def keyPressEvent(self, event):
        #if event.key() == Qt.Key.Key_Escape:
        pass

    def update(self):
        if self.dataContainer.fan_state:
            self.btnFan.setStyleSheet("background-color: rgb(85, 255, 0);")
        else:
            self.btnFan.setStyleSheet("")
        if self.arduinoComm.connected:
            self.lblConnected.setStyleSheet("background-color: rgb(85, 255, 0);")
        else:
            self.lblConnected.setStyleSheet("background-color: rgb(255, 0, 0);")

        if self.dataContainer.sp_reached:
            self.lbl_SP_reached.setStyleSheet("color: rgb(255, 255, 255); background-color: green;")
        else:
            self.lbl_SP_reached.setStyleSheet("")

        self.lblDriverState.setText(f" Stav měniče:{self.dataContainer.driver_state}")
        self.btnStirOnOff.setText("Vypnout" if self.dataContainer.driverRun else "Zapnout")


        self.dataContainer.state_machine_on = self.chk_stateMachine_on.isChecked()
        self.chk_HLT_pid.setChecked(self.dataContainer.hlt_PID)
        self.chk_RVK_pid.setChecked(self.dataContainer.rvk_PID)
        self.chk_HLT_on.setChecked(self.dataContainer.hlt_on)
        self.chk_RVK_on.setChecked(self.dataContainer.rvk_on)

        if self.chk_RVK_pid.isChecked():
            self.e_rvk_sp.setSuffix("°C")
        else:
            self.e_rvk_sp.setSuffix("%")

        if self.chk_HLT_pid.isChecked():
            self.e_hlt_sp.setSuffix("°C")
        else:
            self.e_hlt_sp.setSuffix("%")

        self.lbl_hlt_value.setText("{:.1f} °C".format(self.dataContainer.hlt_value))
        self.lbl_rvk_value.setText("{:.1f} °C".format(self.dataContainer.rvk_value))
        self.lbl_scz_value.setText("{:.1f} °C".format(self.dataContainer.scz_value))

        hlt_error = self.dataContainer.errorFlags & 0x02
        rvk_error = self.dataContainer.errorFlags & 0x04
        scz_error = self.dataContainer.errorFlags & 0x08

        str_error = ""
        str_error += "UNKNOWN" if self.dataContainer.errorFlags & 0x01 else ""
        str_error += "HLT_SENSOR" if hlt_error else ""
        str_error += "RVK_SENSOR" if rvk_error else ""
        str_error += "SCZ_SENSOR" if scz_error else ""

        if hlt_error:
            self.lbl_hlt_value.setStyleSheet("background-color: rgb(255, 0, 0);")
        else:
            self.lbl_hlt_value.setStyleSheet("background-color: rgb(0, 150, 231);")
        if rvk_error:
            self.lbl_rvk_value.setStyleSheet("background-color: rgb(255, 0, 0);")
        else:
            self.lbl_rvk_value.setStyleSheet("background-color: rgb(0, 150, 231);")

        if scz_error:
            self.lbl_scz_value.setStyleSheet("background-color: rgb(255, 0, 0);")
        else:
            self.lbl_scz_value.setStyleSheet("background-color: rgb(0, 150, 231);")

        self.lbl_errors.setText(f"Errors: {self.dataContainer.errorFlags} - {str_error}")

        self.e_hlt_sp.setValue(self.dataContainer.hlt_setpoint)
        self.e_rvk_sp.setValue(self.dataContainer.rvk_setpoint)

        # heating elements
        self.colorify_heating_element(self.dataContainer.outputs & 0x01, self.rvk_heat_1)
        self.colorify_heating_element(self.dataContainer.outputs & 0x02, self.rvk_heat_2)
        self.colorify_heating_element(self.dataContainer.outputs & 0x04, self.rvk_heat_3)

        self.colorify_heating_element(self.dataContainer.outputs & 0x08, self.hlt_heat_1)
        self.colorify_heating_element(self.dataContainer.outputs & 0x10, self.hlt_heat_2)
        self.colorify_heating_element(self.dataContainer.outputs & 0x20, self.hlt_heat_3)

        self.lbl_rem_time.setText(f"Zbývající čas: {(int)(self.stateMachine.step_remaining_time/60)} min {(int)(self.stateMachine.step_remaining_time%60)} s")
        self.lbl_step_actual_time.setText(
            f"Aktuální čas v kroku:{(int)(self.stateMachine.step_actual_time / 60)} min {(int)(self.stateMachine.step_actual_time % 60)} s")

        self.lbl_reached_actual_time.setText(
            f"Akt.čas po dosažení:{(int)(self.stateMachine.step_reached_actual_time / 60)} min {(int)(self.stateMachine.step_reached_actual_time % 60)} s")

        self.lbl_avg_grad.setText(f"Gradient: {'{:.1f} °C'.format(self.dataContainer.avg_grad)}°C/min")

        for l in self.mashLines:
            l.setColor("rgb(0, 150, 255)")
        if len(self.mashLines) > self.stateMachine.state - 1:
            self.mashLines[self.stateMachine.state - 1].setColor("green")

    def colorify_heating_element(self, state, object):
        if state:
            object.setStyleSheet("background-color: rgb(85, 255, 0);")
        else:
            object.setStyleSheet("background-color: rgb(0, 85, 127);")

