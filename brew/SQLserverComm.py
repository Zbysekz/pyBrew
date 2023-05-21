
def SendDataToServer(self):
    global MySQL_Thread
    try:
        # print("Send data to server check")
        if self.first_arduino_data_ready and MySQL_Thread.PersistentConnect():
            data = self.screenManager.dataContainer
            # print("Sending")
            MySQL_Thread.insertValue("temperature", 'hlt_value', data['hlt_value'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=1)
            MySQL_Thread.insertValue("temperature", 'rvk_value', data['rvk_value'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=1)
            MySQL_Thread.insertValue("temperature", 'scz_value', data['scz_value'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=1)
            MySQL_Thread.insertValue("temperature", 'errorFlags', data['errorFlags'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=1)
            MySQL_Thread.insertValue("temperature", 'avg_grad', data['avg_grad'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=0.3)
            MySQL_Thread.insertValue("temperature", 'hlt_setpoint', data['hlt_setpoint'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=1)
            MySQL_Thread.insertValue("temperature", 'rvk_setpoint', data['rvk_setpoint'],
                                     periodicity=60 * MINUTE,
                                     writeNowDiff=1)

            MySQL_Thread.PersistentDisconnect()
    except Exception as e:
        Log("Exception for main SendDataToServer()")
        LogException(e)

    if not self.terminate:
        tmr = threading.Timer(120, self.SendDataToServer)  # calling itself periodically
        tmr.start()
        self.threads["UpdateValuesFromServerThread"] = tmr