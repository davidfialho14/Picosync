from watchdog.events import PatternMatchingEventHandler
import os.path as path
import set_queue as queue

class SyncHandler(PatternMatchingEventHandler):

    def __init__(self, client, directory):
        super().__init__()

        self.client = client
        self.directory = path.normpath(directory)
        # queue with files to update the dropbox server
        self.updateQueue = queue.SetQueue()

    def update(self):
        while not self.updateQueue.empty():
            # get filename from queue
            filename = self.updateQueue.get()

            # ensure the pathname for the file is complete
            # in order to prevent errors indicating a file doesn't exist
            filepath = path.join(self.directory, filename)

            # update file to the dropbox server
            file = open(filepath, "rb")
            self.client.put_file(filename, file, overwrite=True)
            print("file updated in dropbox: ", filename)
            file.close()

            # notify that the current task is done
            self.updateQueue.task_done()

    def on_modified(self, event):
        if not event.is_directory:
            self.updateQueue.put(event.src_path)
            print("updated the file " + event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.updateQueue.put(event.src_path)
            print("added the file " + event.src_path)
