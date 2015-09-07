from watchdog.events import PatternMatchingEventHandler
import os.path as path
import set_queue as queue
import os
from datetime import datetime as datetime
import dropbox
import urllib3

class SyncHandler(PatternMatchingEventHandler):

    def __init__(self, client, watchDirectory, destDirectory):
        super(SyncHandler, self).__init__()

        self.logfileName = os.environ['HOME'] + "/.picosync-log"
        if path.exists(self.logfileName):
            os.remove(self.logfileName)

        self.printLog("started")

        self.client = client
        self.watchDirectory = path.normpath(watchDirectory)
        self.destDirectory = destDirectory
        self.updateQueue = queue.SetQueue()

    def printLog(self, logMessage):
        logFile = open(self.logfileName, "a+")
        logFile.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S\t"))
        logFile.write(logMessage + '\n')
        logFile.close()

    def update(self):

        filesFailed = None

        while not self.updateQueue.empty():
            # get filename from queue
            filename = self.updateQueue.get()

            # ensure the pathname for the file is complete
            # in order to prevent errors indicating a file doesn't exist
            filepath = path.join(self.watchDirectory, os.path.basename(filename))

            # update file to the dropbox server
            file = open(filepath, "rb")

            try:
                self.client.put_file(path.join(self.destDirectory, path.basename(filename)), file, overwrite=True)
                self.printLog("file updated in dropbox: " + filename)
            except dropbox.rest.ErrorResponse, urllib3.exceptions.MaxRetryError:
                self.printLog("connection error will try update later")
                # add file to the list of failed files
                filesFailed.append(filename)

            file.close()

            # notify that the current task is done
            self.updateQueue.task_done()

        if filesFailed:
            # readd failed files to the queue
            for filename in filesFailed:
                self.updateQueue.put(filename)

    def on_modified(self, event):
        if not event.is_directory:
            self.updateQueue.put(event.src_path)
            self.printLog("updated the file " + event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.updateQueue.put(event.src_path)
            self.printLog("added the file " + event.src_path)
