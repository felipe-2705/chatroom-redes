# Python program to implement server side of chat room.
# This is a modified version of https://www.geeksforgeeks.org/simple-chat-room-using-python/ 
import socket 
import select 
import sys 
from _thread import *



class Server():
    
    def __init__(self,IP_address,Port):
        """The first argument AF_INET is the address domain of the 
        socket. This is used when we have an Internet Domain with 
        any two hosts The second argument is the type of socket. 
        SOCK_STREAM means that data or characters are read in 
        a continuous flow."""
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ip_address = IP_address
        self.port = Port
        """ 
        binds the server to an entered IP address and at the 
        specified port number. 
        The client must be aware of these parameters 
        """
        self.conn.bind((self.ip_address, self.port)) 
        """ 
        listens for 100 active connections. This number can be 
        increased as per convenience. 
        """
        self.conn.listen(100) 
        self.list_of_clients = []

        def clientthread(self,conn, addr): 
            # sends a message to the client whose user object is conn 
            conn.send("Welcome to this chatroom!") 

            while True: 
                    try: 
                        message = conn.recv(2048) 
                        if message: 

                            """prints the message and address of the 
                            user who just sent the message on the server 
                            terminal"""
                            print ("<" + addr[0] + "> " + message) 

                            # Calls broadcast function to send message to all 
                            message_to_send = "<" + addr[0] + "> " + message
                            """TODO messages need to be treated to be send to a specific client not to all of them
                            if requeried"""
                            broadcast(message_to_send, conn) 

                        else: 
                            """message may have no content if the connection 
                            is broken, in this case we remove the connection"""
                            remove(conn) 
                    except: 
                        continue

        """Using the below function, we broadcast the message to all 
        clients who's object is not the same as the one sending 
        the message """
        def broadcast(self,message, connection): 
            for clients in self.list_of_clients: 
                if clients!=connection: 
                    try: 
                        clients.send(message) 
                    except: 
                        clients.close() 

                        # if the link is broken, we remove the client 
                        remove(clients) 

        """The following function simply removes the object 
        from the list that was created at the beginning of 
        the program"""
        def remove(self,connection): 
            if connection in self.list_of_clients: 
                self.list_of_clients.remove(connection) 

        """Here we will start the server to accept connection for self.conn socket
        binded to self.ip_address and port"""
        def start(self):
            while True: 
                """Accepts a connection request and stores two parameters, 
                conn which is a socket object for that user, and addr 
                which contains the IP address of the client that just 
                connected"""
                conn, addr = self.conn.accept() 

                """Maintains a list of clients for ease of broadcasting 
                a message to all available people in the chatroom"""
                self.list_of_clients.append(conn) 

                # prints the address of the user that just connected 
                print(f'{addr[0]}: connected')

                # creates and individual thread for every user 
                # that connects 
                start_new_thread(self.clientthread,(conn,addr))

# checks whether sufficient arguments have been provided 
if len(sys.argv) != 3: 
    print ("Correct usage: script, IP address, port number")
    exit() 
# takes the first argument from command prompt as IP address 
IP_address = str(sys.argv[1]) 
# takes second argument from command prompt as port number 
Port = int(sys.argv[2])

## Setting up an server instance 
server = Server(IP_address,Port)
## Starting Server
server.start()
server.conn.close()


