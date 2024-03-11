import mysql.connector
import threading
from datetime import datetime, timezone
import sys
import os

# for periodicity mysql inserts
HOUR = 3600
MINUTE = 60

def ThreadingLockDecorator(func):
    def wrapper(*args, **kwargs):
        # cMySQL.mySQLLock.acquire()
        ret = func(*args, **kwargs)
        # cMySQL.mySQLLock.release()
        return ret

    return wrapper

class SQLcomm:
    mySQLLock = threading.Lock()

    def __init__(self, parameters, dataContainer):
        self._persistentConnection = False
        self.databaseCon = None
        self.terminate = False
        self.threads = {}
        self.dataContainer = dataContainer
        self.parameters = parameters
    def getConnection(self):
        if self._persistentConnection:
            return self.databaseCon, self.databaseCon.cursor()
        else:
            db = self.init_db()
            if db:
                return db, db.cursor()
            else:
                return None, None

    def PersistentConnect(self):
        self.databaseCon = self.init_db()
        if self.databaseCon:
            self._persistentConnection = True
        else:
            self._persistentConnection = False

        return self._persistentConnection

    def PersistentDisconnect(self):
        self._persistentConnection = False
        if self.databaseCon:
            self.databaseCon.close()

    def init_db(self):
        try:
            return mysql.connector.connect(
                host=self.parameters.SERVER_IP_ADDRESS,
                user="screenpi",
                password="screen2448",
                database="db1"
            )
        except mysql.connector.errors.InterfaceError:
            Log("Could not connect to mysql server! - Interface error")
            return None
        except mysql.connector.errors.OperationalError:
            Log("Could not connect to mysql server! - Operational error")
            return None
        except Exception as e:
            Log(f"Could not connect to mysql server! - Other error: {repr(e)}")
            return None

    def closeDBIfNeeded(self, conn):
        if not self._persistentConnection:
            conn.close()

    @ThreadingLockDecorator
    def insertValue(self, name, sensorName, value, timestamp=None, periodicity=0,
                    writeNowDiff=1):
        try:
            db, cursor = self.getConnection()
            if db is None:
                return False

            if not timestamp:  # if not defined, set time now
                timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

            args = (timestamp, name, sensorName, value, periodicity, writeNowDiff)
            res = cursor.callproc('insertMeasurement', args)

            db.commit()
            cursor.close()
            self.closeDBIfNeeded(db)

        except Exception as e:
            Log("Error while writing to database for measurement:" + name + " exception:")
            LogException(e)
            return False

        return True
    def SendDataToServer(self):
        try:
            print("Send data to server check")
            if self.dataContainer.first_arduino_data_ready and self.getConnection():
                data = self.dataContainer
                print("Sending")
                self.insertValue("temperature", 'brewhouse_hlt_value', data.hlt_value,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                self.insertValue("temperature", 'brewhouse_rvk_value', data.rvk_value,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                self.insertValue("temperature", 'brewhouse_scz_value', data.scz_value,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                self.insertValue("temperature", 'brewhouse_errorFlags', data.errorFlags,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                self.insertValue("temperature", 'brewhouse_avg_grad', data.avg_grad,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=0.3)
                self.insertValue("temperature", 'brewhouse_hlt_setpoint', data.hlt_setpoint,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=1)
                self.insertValue("temperature", 'brewhouse_rvk_setpoint', data.rvk_setpoint,
                                         periodicity=60 * MINUTE,
                                         writeNowDiff=1)

                self.PersistentDisconnect()
        except Exception as e:
            Log("Exception for main SendDataToServer()")
            LogException(e)

        if not self.terminate:
            tmr = threading.Timer(120, self.SendDataToServer)  # calling itself periodically
            tmr.start()
            self.threads["SendDataToServerThread"] = tmr

    @ThreadingLockDecorator
    def insertTxCommand(self, destination, data):
        try:
            db, cursor = self.getConnection()
            if db is None:
                return False

            sql = "INSERT INTO TXbuffer (destination, data,timestamp) VALUES (%s, %s,UTC_TIMESTAMP())"
            val = (destination, str(data))
            cursor.execute(sql, val)

            db.commit()
            cursor.close()
            self.closeDBIfNeeded(db)

        except Exception as e:
            Log("Error while writing to database for insertTxCommand:" + destination + " exception:")
            LogException(e)
            return False

        return True

def Log(strr):
    txt = str(strr)
    print("LOG:" + txt)
    dateStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("/var/log/brew/databaseMySQL.log", "a") as file:
        file.write(dateStr + " >> " + txt + "\n")

def LogException(e):
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    Log(str(e))
    Log(str(exc_type) + " : " + str(fname) + " : " + str(exc_tb.tb_lineno))
