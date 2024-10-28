import time

class StateMachine:

    def __init__(self, dataContainer):
        self.state = 1
        self.enabled = False
        self.step_remaining_time = 0
        self.step_actual_time = 0
        self.step_reached_actual_time = 0
        self.dataContainer = dataContainer
        self.step_start_timer = time.time()
        self.step_reached_timer = time.time()
        self.enabled_last = False
        self.tmrAvgGrad = time.time()
        self.lastGradVal = 0.0

    def start(self):
        self.state = 1
        self.step_remaining_time = 0
        self.step_actual_time = 0
        self.step_start_timer = time.time()
        self.step_reached_timer = time.time()
        self.dataContainer.sp_reached = False
    def skipStep(self):
        self.step_start_timer = time.time()
        self.step_reached_timer = time.time()
        self.state += 1
        self.dataContainer.sp_reached = False

    def process(self):
        self.enabled_last = self.enabled
        self.enabled = self.dataContainer.state_machine_on
        self.calculate_process_values()

        if self.enabled:

            if str(self.state) not in self.dataContainer.recipe:
                self.enabled = False
            else:


                step_temp, step_time, step_grad = self.dataContainer.recipe[str(self.state)]

                self.dataContainer.rvk_on = self.dataContainer.rvk_value < step_temp
                self.dataContainer.rvk_PID = False

                if not self.dataContainer.sp_reached:
                    self.dataContainer.rvk_setpoint = step_grad  # for now - without grad regulation
                    reduction = abs(step_temp - self.dataContainer.rvk_value)
                    if reduction <5:
                        self.dataContainer.rvk_setpoint -= (5-reduction) * 20
                        if self.dataContainer.rvk_setpoint < 5:
                            self.dataContainer.rvk_setpoint = 5
                else:
                    self.dataContainer.rvk_setpoint = step_grad * 0.2

                if self.dataContainer.rvk_value >= step_temp-2:
                    if not self.dataContainer.sp_reached:
                        self.dataContainer.sp_reached = True
                        self.step_reached_timer = time.time()

                self.step_actual_time = time.time() - self.step_start_timer
                self.step_remaining_time = step_time*60 - self.step_reached_actual_time

                if self.dataContainer.sp_reached:
                    self.step_reached_actual_time = time.time() - self.step_reached_timer
                else:
                    self.step_reached_actual_time = 0
                if self.step_remaining_time <= 0:
                    self.step_start_timer = time.time()
                    self.step_reached_timer = time.time()
                    self.state += 1
                    self.dataContainer.sp_reached = False

        else:
            if self.enabled_last:
                # was just turned off, so switch off all stuff
                self.dataContainer.rvk_on = False


    def calculate_process_values(self):
        PERIOD = 2  # min
        if time.time() - self.tmrAvgGrad > 60*PERIOD:  # 2 MIN
            self.tmrAvgGrad = time.time()

            self.dataContainer.avg_grad = (self.dataContainer.rvk_value - self.lastGradVal) / PERIOD
            self.lastGradVal = self.dataContainer.rvk_value

