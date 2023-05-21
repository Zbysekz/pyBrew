

class DataContainer:
    def __init__(self):
        self.fan_state = False
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

        self.sp_reached = False

        self.recipe = {}


    def updateValues(self):
        pass

    def calculateGradients(self):
        pass