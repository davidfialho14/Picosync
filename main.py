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

    return userKey

def printHelp():
    print("usage: exec <username> <watch directory> <dropbox directory> <update period>")
    print("*username: dropbox username of the account you are going to use")
    print("watch directory: local directory to watched for new and modified files")
    print("dropbox directory: directory in your dropbox account where the file will be stored")
    print("update period: time interval (in seconds) between updates to the dropbox account")

    print("the arguments with a star (*) are mandatory")

def parseArgs():

    if len(sys.argv) < 2 or len(sys.argv) > 5 or sys.argv[1] == "-h":
        printHelp()
        sys.exit(-1)

    # mandatory argument
    username = sys.argv[1]
    # default watch directory is the current directory
    watchDirectory = str(sys.argv[2]) if len(sys.argv) > 2 else "./"
    # default destination directory
    destDirectory = str(sys.argv[3]) if len(sys.argv) > 3 else "./"
    # default timeout is 30 seconds
    timeout = float(sys.argv[4]) if len(sys.argv) > 4 else 30.0

    return username, watchDirectory, destDirectory, timeout

def main():

    username, watchDirectory, destDirectory, timeout = parseArgs()

    print("username: " + username)
    print("watch directory: " + watchDirectory)
    print("dropbox directory: " + destDirectory)
    print("timeout: %f seconds" % timeout)
    print()

    if not path.exists(watchDirectory) or not path.isdir(watchDirectory):
        print("watch directory doesn't exist")
        print("please check if the path you introduced is a valid directory")
        sys.exit(-1)

    appKey = "1tgi3eh3hq78u34"
    appSecret = "gbme5pduzne981p"

    # authorize the app
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(appKey, appSecret)

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
    syncHandler = monitor.SyncHandler(dropbox.client.DropboxClient(userKey), watchDirectory)

    # schedule the observer
    observer = Observer()
    observer.schedule(syncHandler, watchDirectory)
    observer.start()

    # put the main program waiting for a keyboard interrupt
    try:
        print("running...")
        while True:
            syncHandler.update()
            time.sleep(timeout)
    except KeyboardInterrupt:
        observer.stop()

    print("closing...")
    observer.join()

# start the main
main()
