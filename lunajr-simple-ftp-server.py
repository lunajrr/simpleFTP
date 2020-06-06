import os
import sys
import socket
import threading
import time

#Queues/variables 
connections = []
niceLookingConn = []
active = True



####################################SENDING FILE CODE###################

#method to read data, and send
def sendingFiles(fileName, conn, size):
    f = open(fileName, "r")
    data = f.read()
    data = bytes(data, 'UTF-8')
    conn.send(data)
    print("Finish sending file:", fileName)
    return

#method to get size, send size, and make sure response is correct
def sendFile(fileName, conn):
    #TRY GET FILE SIZE. 
    try:
        size = str(os.path.getsize(fileName))
        sizeCode = bytes(size, 'UTF-8')
        conn.send(sizeCode)
        response = conn.recv(2048).decode()
        if response != "READY":
            print("ERROR:DOWNLOAD - Protocol Error")
            return
        else:
            print("Sending Chunk")
            sendingFiles(fileName, conn, int(size))
            return

    #FILE NOT FOUND ERROR HANDLING
    except FileNotFoundError:
        print("ERROR: Download - File Not Found ")
        conn.send(b'ERROR: Download - File Not Found\n')
        return


####################################SENDING HELP CODE###################
def helpProccess(conn):
    conn.send(b'\nValid Commands \nLS - List files in current directory\nDOWNLOAD - Target file to server (DOWNLOAD <remote file name>)\nUPLOAD - Upload target file to server (UPLOAD <local file name>)\nHELP - List the help options\nQUIT - Terminate the session\n\n')
    return


###################################LIST FILES CODE ######################

#code to list files
def listFiles(conn):
    #variables
    files = ""
    toBeDeleted = "."

    #to get array of files
    listOfFiles = os.listdir(".")
    i = len(listOfFiles)

    #to delete files that starts with . (hidden files)
    while(i > 0):
        if listOfFiles[i-1].startswith("."):
            del listOfFiles[i-1]
        i -= 1
    i = 1

    #Putting list of files into a string to convert to bytes to send
    while(i <= len(listOfFiles)):
        files = files + listOfFiles[i-1] + "\n"
        i+=1
    
    conn.send(bytes(files, 'UTF-8'))
    
######################################CODE TO RECIEVE UPLOADED FILE################################

#METHOD to create and write to file
def creatingFile(data, fileName,fileSize):

    #Try to create file and write data into it
    try:
        f = open(fileName, "w+")
        f.writelines(data)
        print("Writing " + fileName + " to disk")
        f.close()
    except:
        print("Error while creating file: ", fileName)
        
#method to check commands, and file size, and to recieve the data
def recievingFile(data, conn, fileName):

    recieve = 0
    i = 0
    transferSize = 2048
    dataRec = ""

    #Try to convert the list of data recieved from the client
    try:
        fileSize = data[2]
        fileSize = int(fileSize)
    except ValueError:
        conn.send(b"ERROR: UPLOAD - Invalid File Size")
        return
    except IndexError:
        conn.send(b"ERROR: UPLOAD - Invalid Data Recieved")

    #if file size is wrong, cancel
    if(fileSize <= 0):
        conn.send(b"ERROR:UPLOAD - Invalid File Size")
        return

    #if file size is less the the transfer size, do it in one place
    elif(fileSize < transferSize):
        conn.send(b"READY")
        data = conn.recv(transferSize).decode()
        creatingFile(data, fileName,fileSize)
        return

        #if file size is greater then transfer size, raise transfer size then download.
    elif(fileSize >= transferSize):
        transferSize =262144
        conn.send(b"READY")
        while(recieve <= fileSize):
            dataRec += conn.recv(transferSize).decode()
            recieve += transferSize
        creatingFile(dataRec, fileName, fileSize)


    




############################# Communicating w/ Client #########################

def communicate():
    global connections, niceLookingConn
    
    connected = True
    client_add = connections.pop()
    #Gettingip/port looking nice for human use
    ip = str(niceLookingConn.pop())
    ip = ip.replace("', ", ":").replace("('", "").replace(")", "")

    print("*** Accepted connection from ", ip)

    while connected:
        try:
            data = client_add.recv(2048).decode()
        except ConnectionResetError:
            print(ip + " Disconnected")
            return
        if not data:
            print("Client Disconnected: ")
            return
        print("*** Recieved message: " + data + " from " + str(ip))
        print("Recieved Command: ", data )
        data = data.split(" ")
        data[0] = data[0].upper()

        #Checking commands to see if they are valid
        if data[0] == "HELP":
            print("Calling HELP Processor")
            helpProccess(client_add)    

        elif data[0] == "LS":
            print("Calling LS Processor")
            listFiles(client_add)
        
        elif data[0] == "DOWNLOAD":
            print("Calling DOWNLOAD Processor")
            sendFile(str(data[1]), client_add)

        elif data[0] == "UPLOAD":
            print("Calling UPLOAD Processor")
            recievingFile(data, client_add, data[1])

        elif data[0] == "QUIT":
            client_add.close()
            return
        
        




try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print("Error Creating Socket: %s", err)
    print("Closing in 5 seconds")
    time.sleep(5)
    exit()

port = 1337
ip = '0.0.0.0'
ipPort = ip +':'+ str(port)

try:
    s.bind((ip, port)) 
except:
    print("Error binding socket to ", ipPort)
    print("Closing in 5 seconds")
    time.sleep(5)
    exit()

try:
    s.listen()
except:
    print("Error with listening on ", ipPort)
    print("Closing in 5 seconds")
    time.sleep(5)
    exit()

print("Simple FTP SERVER listening on ", ipPort)




while active:
    connection, client_add = s.accept()
    

    try:
        connections.append(connection)
        niceLookingConn.append(client_add)
        #thread
        clientComm = threading.Thread(target=communicate, args=())
    except:
        print("Error adding connection to connection list.")

    clientComm.start()

    
