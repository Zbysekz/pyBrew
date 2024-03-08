import serial
from logger import Log, LogException
import threading
from comm import Receiver, CreatePacket, getRcvdData



cmd_testRead = bytes.fromhex("02030C1E0004")

cmd_readETA = bytes.fromhex("0203219B0001")

cmd_switch_on = bytes.fromhex("020621990007")
cmd_run = bytes.fromhex("02062199000F")
cmd_shutdown = bytes.fromhex("020621990006")
cmd_fault_reset_prep = bytes.fromhex("02062199000F")
cmd_fault_reset = bytes.fromhex("02062199008F")


# Corresponds to CRC-16/MODBUS on https://crccalc.com/
def modbusCrc(msg:str) -> int:
    crc = 0xFFFF
    for n in range(len(msg)):
        crc ^= msg[n]
        for i in range(8):
            if crc & 1:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc

def printByteList(data):
    strx = " ".join([f"{x:02x}" for x in data])
    Log(f"{strx}")

def createPacket(data):
    crc = modbusCrc(data)
    #print(f"CRC:{crc:02x}")

    data += crc.to_bytes(length=2, byteorder="little")

    return data

def decode_ETA(data):
    if len(data) > 4:
        if data[0] == 0x02 and data[1] == 0x03:
            eta = data[3]*256 + data[4]
            Log(f"ETA is:0x{eta:02x}")
            return eta
    return -1;
    Log(f"error decoding ETA!")

def ETA2TEXT(eta):
    if eta == 0x33:
        return 'switched_on'
    elif eta == 0x31:
        return 'ready_to_switch_on'
    return f'{eta:02x}'

class DriverComm:
    def __init__(self, parameters, threads, dataContainer):
        self.connected = False
        self.terminate = False
        self.parameters = parameters
        self.serialPort = None
        self.threads = threads
        self.dataContainer = dataContainer
        self.driver_on = False
        self.tx_commands = []

    def send_tx(self, packet):
        self.tx_commands.append(createPacket(packet))

    def CheckSerialPortOpened(self):
        try:
            self.serialPort = serial.Serial(self.parameters.DRIVER_SERIALPORT, baudrate=19200, stopbits=1, parity="E",
                                            timeout=0.1)  # open serial port
            self.connected = True
            Log("Serial port for driver opened.")
        except Exception as e:
            Log("Serial port opening error! " + str(e))

    def process(self):
        try:
            if self.connected:
                self.ProcessIncomeData()
            else:
                self.CheckSerialPortOpened()
        except Exception as e:
            LogException(e)
        if not self.terminate:
            tmr = threading.Timer(1, self.process)  # calling itself periodically
            tmr.start()
            self.threads["driverSerialPortThread"] = tmr
        else:
            if self.connected:
                self.serialPort.close()

    def CmdReset(self):
        print("sending two!")
        self.send_tx(cmd_fault_reset_prep)
        self.send_tx(cmd_fault_reset)
        print(self.tx_commands)

    def CmdTurnOn(self):
        if not self.dataContainer.driverRun:
            self.dataContainer.driverRun = 1
        else:
            self.dataContainer.driverRun = 0

        #self.send_tx(cmd_run)

    def CmdSPChanged(self):
        speed = self.dataContainer.driver_sp
        Log(f"Sending speed:{speed}")
        speed_sp = bytes.fromhex("0206219A") + speed.to_bytes(length=2, byteorder="big")
        self.send_tx(speed_sp)

    def ProcessIncomeData(self):
        container = self.dataContainer

        if len(self.tx_commands):
            while(len(self.tx_commands)):
                sent_cmd = self.tx_commands.pop(0)
                self.serialPort.write(sent_cmd)

                rcv_data = []
                char = self.serialPort.read()
                while char:
                    rcv_data += char
                    char = self.serialPort.read()
                rcv_data = bytes(rcv_data)
                if rcv_data != sent_cmd:
                    Log("Sending tx failure!")
                    Log(rcv_data)
                    Log(sent_cmd)
                else:
                    Log("send command OK!")
        else:
            self.serialPort.write(createPacket(cmd_readETA))
            rcv_data = []
            char = self.serialPort.read()
            while char:
                rcv_data += char
                char = self.serialPort.read()
            if len(rcv_data) > 1:
                printByteList(rcv_data)
                driver_state = decode_ETA(rcv_data)

                if driver_state >= 0:
                    container.driver_state = ETA2TEXT(driver_state)