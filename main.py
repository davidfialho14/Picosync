import dropbox
import os.path as path
import sys
import time
from watchdog.observers import Observer
import monitor

keysFilename = ".keys"

def authorizeDropbox(flow):
    # Have the user sign in and authorize this token
    authorizeUrl = flow.start()
    print('1. Go to: ' + authorizeUrl)
    print('2. Click "Allow" (you might have to log in first)')
    print('3. Copy the authorization code.')
    code = input("Enter the authorization code here: ").strip()

    # This will fail if the user enters an invalid authorization code
    userKey, userId = flow.finish(code)

    return userKey

def getUserKey(username):
    userKey = ""    # variable to be returned with the user key

    if path.exists(keysFilename):
        # open keys file
        keysFile = open(keysFilename, "r")

        # get user key from the keys file for the given username
        for line in keysFile.readlines():
            index = line.find(":")
            lineUsername = line[:index]     # the username is stored previous to the first ':' char
            lineKey = line[index + 1:]      # the user key is stored after the first ':' char

            # check if the correct username was found
            if lineUsername == username:
                # username found -> get access token
                userKey = lineKey
                # leave the loop
                break

        keysFile.close()

    return userKey, 0

def parseArgs():
    defaultDirectory = "./"    # default directory is the current directory
    defaultTimeout = 30        # default timeout is 30 seconds

    if len(sys.argv) == 1:
        directory = defaultDirectory
        timeout = defaultTimeout
    elif len(sys.argv) == 2:
        directory = str(sys.argv[1])
        timeout = defaultTimeout
    elif len(sys.argv) == 3:
        directory = str(sys.argv[1])
        timeout = float(sys.argv[2])
    else:
        print("usage: exec <watch directory> <update period")
        sys.exit(-1)

    return directory, timeout

def main():

    directory, timeout = parseArgs()

    if not path.exists(directory) or not path.isdir(directory):
        print("usage: exec <watch directory>")
        sys.exit(-1)

    appKey = "1tgi3eh3hq78u34"
    appSecret = "gbme5pduzne981p"

    # authorize the app
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appKey, appSecret)

    # get user name to identify the login
    username = input("dropbox username: ")

    # check the database for the user key
    userKey = getUserKey(username)

    if not userKey:
        # user key was not found -> new user
        # get new user authorization
        userKey = authorizeDropbox(flow)

        # save access token
        keysFile = open(keysFilename, "w")
        keysFile.write(username + ":" + userKey)
        keysFile.flush()
        keysFile.close()

    # get a sync handler
    syncHandler = monitor.SyncHandler(dropbox.client.DropboxClient(userKey), directory)

    # schedule the observer
    observer = Observer()
    observer.schedule(syncHandler, directory)
    observer.start()

    # put the main program waiting for a keyboard interrupt
    try:
        while True:
            syncHandler.update()
            time.sleep(timeout)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

# start the main
main()
