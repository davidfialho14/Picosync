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

def main():
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

    # get a dropbox client for the access token
    client = dropbox.client.DropboxClient(userKey)

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
