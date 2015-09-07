import os
import sys
from datetime import datetime

# app directory - where all managing file are saved
appDirectory = os.path.join(os.environ['HOME'], ".picosync")

# the logs are stored in a log directory
# the name of the log indicate the date and time when the app was started
logDirectory = os.path.join(appDirectory, "logs")
logFileName = os.path.join(logDirectory, datetime.now().strftime("%Y%m%d-%H:%M:%S") + ".log")

# prints the message to the app log file and to the output
# before printing the message it prints the time and date when the message was written
def printLog(logMessage):
    logFile = open(logFileName, "a+")
    logFile.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S\t"))
    logFile.write(logMessage + '\n')
    print(logMessage)
    logFile.close()

# the app and log directories are created
# if there is any new directory that needs to be created it should be created inside this function
def createAllDirectories():
    if not os.path.exists(appDirectory):
        # create the app directory
        os.mkdir(appDirectory)
    else:
        if not os.path.isdir(appDirectory):
            print("the app directory (%s) exists but is not a directory" % appDirectory)
            print("please remove this directory and restart the app")
            sys.exit(-1)

    if not os.path.exists(logDirectory):
        # create log directory
        os.mkdir(logDirectory)
    else:
        if not os.path.isdir(logDirectory):
            # remove the file that should be a directory and create a directory
            os.remove(logDirectory)
            os.mkdir(logDirectory)

