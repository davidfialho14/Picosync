from watchdog.events import PatternMatchingEventHandler
import os.path as path

class SyncHandler(PatternMatchingEventHandler):

    def __init__(self, client, directory):
        super().__init__()

        self.client = client
        self.directory = path.normpath(directory)

    def update(self, filename):
        # ensure the pathname for the file is complete
        # in order to prevent errors indicating a file doesn't exist
        filename = path.join(self.directory, filename)

        # update file to the dropbox server
        file = open(filename, "rb")
        response = self.client.put_file(path.basename(filename), file, overwrite=True)
        file.close()

    def on_modified(self, event):
        if not event.is_directory:
            self.update(event.src_path)
            print("updated the file " + event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.update(event.src_path)
            print("added the file " + event.src_path)
