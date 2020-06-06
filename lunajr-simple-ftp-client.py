import os
import sys
import socket
import threading
import time

###################UPLOAD CODE###############

#method to open file, and send the data.
def sendingFiles(fileName, conn, size):

    f = open(fileName, "r")
    data = f.read()
    data = bytes(data,'UTF-8')
    print ("Sending chunks")
    conn.send(data)
    print ("Done sending File:" , fileName)
    return

#Method get size of file, and send command with the file size.
def upload(input, conn, fileName):
    try:
        size = str(os.path.getsize(fileName))
        command = bytes(input + " " + size, 'UTF-8')
        conn.send(command)

        #To make sure response is "READY"
        response = conn.recv(2048).decode()
        if response != "READY":
            print("ERROR:UPLOAD - Protocol Error")
            return
        else:
            sendingFiles(fileName, conn, int(size))
            return

    #FILE NOT FOUND ERROR HANDLING
    except FileNotFoundError:
        print ("ERROR:UPLOAD - File not found: " , fileName)
        return

###############HELP CODE########################

def help(conn):
    print(str(conn.recv(2048).decode()))


###############LIST REQUEST CODE ##############

def recievingList(conn):
    
    print ("\nAvailable Files")
    print (str(conn.recv(2048).decode()))


############### DOWNLOAD CODE ###############

def creatingFile(data, fileName,fileSize):


    #Try to create file and write data into it
    try:
        f = open(fileName, "w+")
        f.writelines(data)
        print ("Writing " + fileName +" to disk")
        f.close()
    except:
        print("Error while creating file: ", fileName)
        
#method to recieve and check filesize
def recievingFile(data, conn, fileName):
    recieve = 0
    transferSize = 2048
    dataRec = ""
    

    dataSending = bytes(data, 'UTF-8')
    conn.send(dataSending)
    fileSize = conn.recv(2048).decode()
    try:
        fileSize = int(fileSize)
    except ValueError:
        print(fileSize)
        return
    #if file size is wrong, cancel
    if(fileSize <= 0):
        print("ERROR:DOWNLOAD - Invalid File Size")
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

        #Keep on recieving Data until the size has been reached
        while(recieve <= fileSize):
            dataRec += conn.recv(transferSize).decode()
            recieve += transferSize
        creatingFile(dataRec, fileName, fileSize)



################COMMUNICATING WITH SERVER CODE################

#Method that sends the connected and keeps it in a loop
def serverCommunicating(conn):
    #connected is set to true by default
    connected = True

    while connected:
        #Asks for input
        inputData = input("Enter Command: ")

        #Splits input by space, to check for mutiple arguments
        inData = inputData.split(" ")
        #UPPER CASES THE COMMAND(in case of "Download" <fileName> is kept orignal. Windows treats upper/lower case as the same but linux differates)
        inData[0] = inData[0].upper()
        
        ####Checks for Commands
        if(inData[0] == "DOWNLOAD"):
            #if the command has two arguments, then start the file download process. Else print error
            if (len(inData) == 2 and inData[1] != ""):
                recievingFile(inputData, conn, inData[1])
            else:
                print("DOWNLOAD requires 1 element <fileName>\n")
        elif(inData[0] == "UPLOAD"):
            #if the command has two arguments, then start the file UPLOAD process. Else print error
            if (len(inData) == 2 and inData[1] != ""):
                upload(inputData, conn, inData[1])
            else:
                print("UPLOAD requires 1 element <fileName>\n")
        else:

            #if command is 'LS', prepare to recieve List method
            if(inData[0] == "LS"):
                inputData = bytes(inputData,'UTF-8')
                conn.send(inputData)
                recievingList(conn)

            #if command is "HELP", prepare to recieve Help info method
            elif(inData[0] == "HELP"):
                inputData = bytes(inputData,'UTF-8')
                conn.send(inputData)
                help(conn)

            #if command is 'UPLOAD', prepare to upload method
            elif(inData[0] == "QUIT"):
                inputData = bytes(inputData,'UTF-8')
                conn.send(inputData)
                connected = False
                print("Quiting client Program")

            else:
                print ("Invalid Command: " , inputData)
                print ("Use HELP to get a list of valid commands\n")
    

########################SOCKET CODE########################

#CREATING SOCKET

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error as err:
    print("Error Creating Socket: %s", err)
    print("Closing in 5 seconds")
    time.sleep(5)
   

port = 1337

try: 
    s.connect(("127.0.0.1", port))
except:
    print("Error connecting with port 1337")
    print("Closing in 5 seconds")
    time.sleep(5)
    exit(0)

#START server communicating
serverCommunicating(s)
s.close()



