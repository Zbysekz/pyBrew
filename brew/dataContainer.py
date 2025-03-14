

class DataContainer:
    def __init__(self):
        self.fan_state = False
        self.water_cooling_state = False
        self.avg_grad = 0.0

        self.state_machine_on = False
        self.hlt_on = False
        self.rvk_on = False
        self.hlt_PID = False
        self.rvk_PID = False

        self.hlt_setpoint = 0.0
        self.rvk_setpoint = 0.0
        self.hlt_value = 0.0
        self.rvk_value = 0.0
        self.scz_value = 0.0

        self.errorFlags = 0
        self.outputs = 0
        self.sensor_error_cnt = 0

        self.sp_reached = False

        self.recipe = {}
        self.driver_state = "?"
        self.driverRun = 0
        self.first_arduino_data_ready = False


    def updateValues(self):
        pass

    def calculateGradients(self):
        pass