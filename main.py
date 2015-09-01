import dropbox
import os.path as path
import sys
import time
from watchdog.observers import Observer
import monitor

def authorizeDropbox(flow):
    # Have the user sign in and authorize this token
    authorizeUrl = flow.start()
    print('1. Go to: ' + authorizeUrl)
    print('2. Click "Allow" (you might have to log in first)')
    print('3. Copy the authorization code.')
    code = input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    accessToken, userId = flow.finish(code)

    return accessToken


def main():
    appKey = "1tgi3eh3hq78u34"
    appSecret = "gbme5pduzne981p"

    # authorize the app
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appKey, appSecret)

    if path.exists(".keys"):
        # get access token from file
        accessToken = open(".keys", "r").readline()

    else:
        accessToken = authorizeDropbox(flow)

        # save access token
        open(".keys", "w").write(accessToken)

    # get a dropbox client for th access token
    client = dropbox.client.DropboxClient(accessToken)

    # remove the first argument from the sys args
    args = sys.argv[1:]

    # schedule the observer
    observer = Observer()
    observer.schedule(monitor.SyncHandler(client), args[0] if args else '.')
    observer.start()

    # put the main program waiting for a keyboard interrupt
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

# start the main
main()
