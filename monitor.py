from watchdog.events import PatternMatchingEventHandler
import dropbox
import os.path as path

class SyncHandler(PatternMatchingEventHandler):
    patterns = ["*.CSV"]

    def __init__(self, client):
        super().__init__()

        self.client = client

    def update(self, filename):
        file = open(filename, "rb")
        response = self.client.put_file(filename, file, overwrite=True)

    def on_modified(self, event):
        if not event.is_directory:
            self.update(event.src_path)
            print("updated the file " + event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.update(event.src_path)
            print("added the file " + event.src_path)
