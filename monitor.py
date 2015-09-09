from watchdog.events import PatternMatchingEventHandler
import os.path as path
import set_queue as queue
import os
import dropbox
import urllib3
import log

class SyncHandler(PatternMatchingEventHandler):

    def __init__(self, client, watchDirectory, destDirectory):
        super(SyncHandler, self).__init__()

        self.client = client
        self.watchDirectory = path.normpath(watchDirectory)
        self.destDirectory = destDirectory
        self.updateQueue = queue.SetQueue()

    def update(self):

        filesFailed = []

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
                log.printLog("file updated to dropbox: " + filename)
            except (urllib3.exceptions.MaxRetryError, dropbox.rest.ErrorResponse):
                log.printLog("failed to upload: " + filename)
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
            log.printLog("updated the file " + event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.updateQueue.put(event.src_path)
            log.printLog("added the file " + event.src_path)
