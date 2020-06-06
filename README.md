# simpleFTP
a simple file transfer protocol

# Server
  Run the server code first. It sets up a socket to recieve connections. Once a connection is accepted, the server waits for       inputs such as Upload, help, download, etc. The sever then processes the command and does the respective methods.
  
#Client
  The client code creates a socket to attempt to connect to the server. Then the client then issues a command and checks to see if the command is valid. If the command is valid, the command is then issued to the server. The server then responds and the cycle continues.
  
  
#Commands

  -HELP: Help is sent to the server from the client through the socket. The Server then processes the help command and sends back the list of valid commands. The Client then outputs the data recieved.
  
  -UPLOAD <FileName>: The Client checks to make sure the file is a valid file. If the file is not valid, an error is then issued to the client instead of sending it to the server. Then once the file is validated, The client sends the command, file name and the size of the file to the server. The server sends back "ready" if the server is ready. If the client recieves anything besides ready, then the upload is stopped and an error is issued. Otherwise, the file is uploaded and confirmation is sent.
  
  -DOWNLOAD <FileName>: the client sends the command and the file name to the server. The server checks to see if the filename is valid and issues a error if its not. Otherwise, the file size is sent and the client then sends "ready" back to server, and the server sends the file to the client. Once download is complete, confirmation is sent.
  
  -LS: List the files in the directory. Command is issued to the server then the server checks the files in its directory and removing hidden files. The server then sends the client the list of file names and the client prints them to the screen.
  
  -QUIT: Exit the program from client side. The client sends the command to the server and the server closes the connection. The client then closes the socket on its side and exits the program.
