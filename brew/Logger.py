from datetime import datetime
from parameters import Parameters
import pathlib
import sys
import os
import traceback

rootPath = str(pathlib.Path(__file__).parent.absolute())

def Log(s, _verbosity=Parameters.NORMAL):
    if _verbosity > Parameters.verbosity:
        return
    print(str(s))

    dateStr = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open("/var/log/brew/main.log", "a") as file:
        file.write(dateStr + " >> " + str(s) + "\n")

def LogException(e):

    Log(traceback.format_exc())

    # exc_type, exc_obj, exc_tb = sys.exc_info()
    # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    # Log(str(e))
    # Log(str(exc_type) +" : "+ str(fname) + " : " +str(exc_tb.tb_lineno))
