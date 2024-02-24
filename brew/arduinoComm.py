import serial
from logger import Log, LogException
import threading
from comm import Receiver, CreatePacket, getRcvdData

def getVal(data, idx):
    return (data[idx] * 256 + data[idx + 1]) / 100.0


def getBytes(val):
    return bytes([int(round(val * 100) / 256), int(round(val * 100)) % 256])


def packBits(*bits):
    result = 0
    position = 0
    for b in bits:
        if b:
            result += (1 << position)
        position += 1
    return bytes([result & 0xFF, (result & 0xFF00) >> 8])

class ArduinoComm:
    def __init__(self, parameters, threads, dataContainer):
        self.connected = False
        self.terminate = False
        self.parameters = parameters
        self.receiver = Receiver()
        self.serialPort = None
        self.threads = threads
        self.dataContainer = dataContainer

        self.HandleSerialPort()

    def process(self):
        if self.connected:
            self.SendData()
            self.ProcessIncomeData()
        else:
            self.CheckSerialPortOpened()

    def CheckSerialPortOpened(self):
        try:
            self.serialPort = serial.Serial( self.parameters.SERIALPORT, timeout=0.1)  # open serial port
            self.connected = True
            Log("Serial port for arduino opened.")
        except Exception as e:
            Log("Serial port opening error! " + str(e))

    def HandleSerialPort(self):
        try:
            if self.connected:
                done = False
                while not done and not self.terminate:
                    try:
                        char = self.serialPort.read(1)
                    except serial.serialutil.SerialException:
                        Log("Lost serial port!")
                        self.connected = False
                        break
                    if len(char) < 1 or char == b'':
                        done = True
                    else:
                        self.receiver.Receive(char[0])
        except Exception as e:
            LogException(e)
        if not self.terminate:
            tmr = threading.Timer(0.5, self.HandleSerialPort)  # calling itself periodically
            tmr.start()
            self.threads["serialPortThread"] = tmr
        else:
            if self.connected:
                self.serialPort.close()

    def SendData(self):

        bitsPacked = packBits(self.dataContainer.hlt_on,
                              self.dataContainer.hlt_PID,
                              self.dataContainer.rvk_on,
                              self.dataContainer.rvk_PID,
                              self.dataContainer.driverRun)
        # print("PACKED:")
        # print([i for i in bitsPacked])
        # print(int.from_bytes(bitsPacked[0],"little",signed=False))

        data = bytes([1]) + bitsPacked + getBytes(
            self.dataContainer.hlt_setpoint) + \
               getBytes(self.dataContainer.rvk_setpoint)

        pkg = CreatePacket(data)
        # print(pkg)

        self.serialPort.write(pkg)

    def ProcessIncomeData(self):
        container = self.dataContainer

        while True:  # process all data
            if self.connected:
                data = getRcvdData()
                # print("received:"+str(data))

                if len(data) > 0:
                    if data[0] == 1:
                        container.hlt_value = getVal(data, 1)
                        container.rvk_value = getVal(data, 3)
                        container.scz_value = getVal(data, 5)

                        container.errorFlags = (int)(getVal(data, 7)) + (
                                    (int)(getVal(data, 9)) << 16)
                        container.outputs = (int)(data[11])

                        self.first_arduino_data_ready = True
                else:
                    break
            else:
                container.hlt_value = 0
                container.rvk_value = 0
                container.scz_value = 0
                container.errorFlags = 0
                container.outputs = 0
                break
