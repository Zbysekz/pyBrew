from datetime import datetime
from parameters import Parameters
import pathlib
import sys
import os
import traceback

rootPath = str(pathlib.Path(__file__).parent.absolute())

parameters = None

def Log(s, _verbosity=Parameters.NORMAL, filename = "main"):
    if _verbosity > parameters.VERBOSITY:
        return
    print(str(s))

    dateStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    path = "/var/log/brew/"+str(filename)+".log"

    try:
        with open(path, "a") as file:
            file.write(dateStr + " >> " + str(s) + "\n")
    except FileNotFoundError:
        with open(path, "x") as file:
            file.write(dateStr + " >> " + str(s) + "\n")

def LogException(e):

    Log(traceback.format_exc())

    # exc_type, exc_obj, exc_tb = sys.exc_info()
    # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    # Log(str(e))
    # Log(str(exc_type) +" : "+ str(fname) + " : " +str(exc_tb.tb_lineno))

def setParameters(pars):
    global parameters
    parameters = pars