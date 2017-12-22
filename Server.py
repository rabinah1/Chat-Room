# This file contains the code for the server of the project.

import socket, sys, select
import time

def broadcast(data, serversocket, serversocket_2): # We use this function to send a message to all users that are connected to the server.
    for socket in READABLE: # Loop through the sockets of all users.
        if socket != serversocket and socket != serversocket_2: # Here we make sure that the server does not send the message to itself.
            if type(data) == list: # If the parameter "data" contains a list of all users connected to the server.
                try:
                    temp2 = "A" # The letter "A" tells the client program that the information coming after this letter must be printed to the rightmost screen of the UI.
                    temp2 = temp2.encode() # We transfer the message to binary form for sending.
                    socket.sendall(temp2)
                    time.sleep(0.05) # Wait for 0.05 seconds so that this message is kept distinct of the next message. If there is no time dealy, multiple different messages will be interpreted as one.
                    temp2 = temp2.decode("ascii") # We transfer temp2 back to ascii-form.
                    temp = "Users online:\n\n"
                    temp = temp.encode()
                    socket.sendall(temp)
                    temp = temp.decode("ascii")

                    # Here we loop through every cell i of the list data (i itself is also a list containing the nickname and IP-address of the user).
                    for i in data:
                        i[0] = i[0].encode() # i[0] contains the nickname of the user.
                        i[1] = i[1].encode() # i[1] contains the IP-address of the user.
                        socket.sendall(i[0])
                        time.sleep(0.02) # Wait for 0.02 seconds so that the nickname and IP-address are kept distinct.
                        socket.sendall(i[1])
                        time.sleep(0.02)
                        i[0] = i[0].decode("ascii")
                        i[1] = i[1].decode("ascii")
                        enter = "\n"
                        enter = enter.encode()
                        socket.sendall(enter)
                        enter = enter.decode("ascii")
                    time.sleep(0.02)
                    temp2 = "B" # The letter "B" tells the client program that the information coming after this letter must be printed to the leftmost screen of the UI.
                    temp2 = temp2.encode()
                    socket.sendall(temp2)
                    time.sleep(0.05)
                    temp2 = temp2.decode("ascii")
                except: # If there was an error in sending a message, we conclude that a ther user has exited, and we close the socket of this user.
                    socket.close()
                    if socket in READABLE:
                        READABLE.remove(socket)
            else: # If the parameter "data" does not contain a list, we are sending a string (= a message of a user) to all clients.
                try:
                    socket.sendall(data) # Send the string to all clients.
                except:
                    socket.close()
                    if socket in READABLE:
                        READABLE.remove(socket)

READABLE = []
WRITEABLE = []
ERROR = []
host = socket.gethostbyname('0.0.0.0') # 0.0.0.0 corresponds to all the IPv4-addresses on the computer that runs the server.
host_2 = '::' # :: corresponds to all the IPv6-addresses on the computer that runs the server.
port_2 = 9005 # The clients using IPv6 connect to port 9005.
port = 9009 # The clients using IPv4 connect to port 9009.
user_list = [] # This is a list that will contain the nicknames and IP-addresses of the users.

try: # Trying to create a socket.
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # The socket using IPv4.
    serversocket_2 = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # The socket using IPv6.
except: # If there was an error creating the server.
    print("Could not start the server.")
    sys.exit()
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Define some settings of the socket.
serversocket_2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind((host, port)) # This command "binds" the address and the port together.
serversocket_2.bind((host_2, port_2))
serversocket.listen(10) # We set the socket to listen for clients. This socket can server a maximum of 10 clients simultaneously.
serversocket_2.listen(10)
READABLE.append(serversocket) # We add the created socekt to a list that contains all the sockets from which we can read something.
READABLE.append(serversocket_2)


while True: # In this loop we will listen for contacts from the cliens.
    try:
        ready_to_read, ready_to_write, in_error = select.select(READABLE,WRITEABLE,ERROR,0) # By using the select-function, we can listen to multiple sockets simultaneously.
    except:
        break
    
    for sock in ready_to_read: # Loop through all the sockets that contain something to be read.
        
        if sock == serversocket: # If a new client using IPv4 tries to connect to the server.
            clientsocket,addr = serversocket.accept() # We accept the connection and return the socket and the IP-address.
            READABLE.append(clientsocket)
            nick = clientsocket.recv(4096).decode("ascii") # We receive a message from the client that contains the nickname of the user.
            user_list.append([nick, addr[0]]) # We add to the list "user_list" the nickname and the IP-address of the user.
            data = "User " + nick + " with ip " + addr[0] + " has joined.\n" # Create a message that contains the nickname and the IP-address of the user.
            data = data.encode()
            broadcast(user_list, serversocket, serversocket_2) # We send the "user_list" to all clients so that the clients can read the nicknames and IP-addresses of the users.
            broadcast(data, serversocket, serversocket_2)
            
        elif sock == serversocket_2: # If a new client using IPv6 tries to connect to the server.
            clientsocket,addr = serversocket_2.accept()
            READABLE.append(clientsocket)
            nick = clientsocket.recv(4096).decode("ascii")
            user_list.append([nick, addr[0]])
            data = "User " + nick + " with ip " + addr[0] + " has joined.\n"
            data = data.encode()
            broadcast(user_list, serversocket, serversocket_2)
            broadcast(data, serversocket, serversocket_2)
            
        else: # If we receive a message from some client.
            try:
                data = sock.recv(4096) # We receive the message and save it to a variable "data".
                data = data.decode("ascii")
                if data[0:10] == "USEREXIT()": # If the message contains a notification that the user exits the program.
                    sock.close() # We close the socket of the client.
                    READABLE.remove(sock)
                    n = 0
                    quit_nick = data[10:len(data)] # We read the nickname of the user and store it to a variable "quit_nick".
                    data = data.encode()
                    for alkio in user_list: # Loop through all the cells (lists containing nickname and IP) in a list, that contains all the clients.
                        if user_list [n][0] == quit_nick: # If the nickname of a user corresponds to the nickname of the user that is exiting.
                            user_list.remove(user_list[n]) # Remove the corresponding user from the list "user_list".
                            broadcast(user_list, serversocket, serversocket_2)
                            data = "User " + quit_nick + " has left."
                            data = data.encode()
                            broadcast(data, serversocket, serversocket_2) # Send a message that tells that the user with nickname <quit_nick> has exited.
                            break
                        else:
                            n = n + 1
                else:  # If the received message contains an ordinary string.
                    data = data.encode()
                    broadcast(data, serversocket, serversocket_2) # Send this string to all clients.
            except: # If we could not receive the data, we conclude that the user has exited and we close the socket of that user.
                sock.close()
                if sock in READABLE:
                    READABLE.remove(sock)
                    break
            
serversocket.close()
serversocket_2.close()
