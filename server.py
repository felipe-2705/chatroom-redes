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
        self.list_of_commands = ['MSG','MSG_ALL','LOGIN','LOGOFF','LIST']


    def get_client(self,client_id):
        for client in self.list_of_clients:
            if client.client_id == client_id:
                return client
        return None

    def authenticate(self,client_id):
        """We will check if client with client_id exists,
        otherwise the client is not authenticated yet"""
        client = self.get_client(client_id)
        if client == None:
            return False
        else:
            return True

    def islogged(self,client):
        if client.client_id != None: 
            return True
        else:
            print(f'< Server > {client.addr} is not logged and can not send any message')
            message = "You are not logged!!!"
            client.send(message)
            return False 

    def clientthread(self,client): 
        # sends a message to the client whose user object is conn 
        client.send("Welcome to this chatroom!") 

        while True: 
            try: 
                message = client.receive() 
                if message: 
                    command, msg = self.parse_command(message.rstrip('\n'))
                    
                    if command == 'LOGIN': 
                        """If Command is login we need to split client_id 
                        from password and try to authenticate the client
                        if Client already authenticated the requests fail
                        """
                        split_msg = msg.split()
                        client_id =  split_msg[0]
                        password = split_msg[1]
                        if self.authenticate(client_id):
                            print(f"< Server > AUTHENTICATION ERROR for {client.addr[0]}")
                            client.send("AUTHENTICATION ERROR")
                        else:
                            client.login(client_id,password)
                            client.send("AUTHENTICATION COMPLETED")
                            self.msg_all('joinned chatroom',client)
                    if command == 'LOGOFF':
                        """If command if logoff we need to identify the client_id
                        then close connection and remove it from server list_of_clients"""
                        if self.islogged(client):
                            client_id =  msg
                            client.conn.close()
                            self.remove(client)
                            self.msg_all('left chatroom',client) 
                    if command == 'MSG':
                        """If command is msg we need to identify the client_dest
                        then send the message"""
                        if self.islogged(client):
                            split_msg = msg.split(' ',1)
                            client_id = split_msg[0]
                            msg = split_msg[1]
                            client_dest = self.get_client(client_id)
                            if client_dest:
                                """prints the message and address of the 
                                user who just sent the message on the server 
                                terminal"""
                                self.msg(msg,client,client_dest)
                            else:
                                response = f'< Server > client_id {client_id} does not exist'
                                client.send(response)
                                print(response)
                    if command == 'MSG_ALL':
                        """If command is msg_all we need to only send the message to all clients 
                        who are not client sender"""  
                        if self.islogged(client):  
                            self.msg_all(msg, client) 
                    if command == 'LIST':
                        """If command is list we need to get all clients logged in
                        who are not the requester"""
                        if self.islogged(client):
                            self.list(client)
                else: 
                    """message may have no content if the connection 
                    is broken, in this case we remove the connection"""
                    self.remove(client) 
            except: 
                continue

    """Using the below function, we broadcast the message to all 
    clients who's object is not the same as the one sending 
    the message """
    def msg_all(self,message, client): 
        message_format = f'< {client.client_id} > {message}'
        print(message_format)
        for client_dest in self.list_of_clients: 
            if client_dest!=client: 
                try: 
                    client_dest.send(message_format)
                except: 
                    client_dest.conn.close() 
                    # if the link is broken, we remove the client 
                    self.remove(client_dest) 

    """Using the below function, we send the message to specified dest
    client"""
    def msg(self,message,client_source,client_dest):
        message_format = f'< {client_source.client_id} > {message}'
        if client_source != client_dest:
            try:
                client_dest.send(message_format)
                print(f'< {client_source.client_id} > {message_format}')
            except:
                client_dest.conn.close()
                # if the link is broken, we remove the client 
                self.remove(client_dest)
                print("< Server > Connection Error, Removing Client ...")
        else:
            print("< Server > Error client source is same as client dest")

    """List command will list all connected clients
    except the requester"""
    def list(self,client):
        client_id_list = []
        for c in self.list_of_clients:
            if c.client_id != client.client_id:
                client_id_list.append(c.client_id)
        
        message_format = f'< Server > {client_id_list}'
        try:
            client.send(message_format)
            print(message_format)
        except:
            client.conn.close()
            # if the link is broken, we remove the client 
            self.remove(client)

    def validate_command(self,command):
        if command in self.list_of_commands:
            return True
        else:
            return False

    def parse_command(self,sentance):
        split_command = sentance.split(" ",1)
        if self.validate_command(split_command[0]):
            command = split_command[0]
            message = None
            if command != 'LIST':
                message = split_command[1]
            return command, message
        else:
            print(f'< {split_command[0]} > is not a valid command')


    """The following function simply removes the object 
    from the list that was created at the beginning of 
    the program"""
    def remove(self,client): 
        if client in self.list_of_clients: 
            self.list_of_clients.remove(client) 

    """Here we will start the server to accept connection for self.conn socket
    binded to self.ip_address and port"""
    def start(self):
        print("Server Started")
        while True: 
            """Accepts a connection request and stores two parameters, 
            conn which is a socket object for that user, and addr 
            which contains the IP address of the client that just 
            connected"""
            conn, addr = self.conn.accept() 

            client = Client(addr,conn)

            """Maintains a list of clients for ease of broadcasting 
            a message to all available people in the chatroom"""
            self.list_of_clients.append(client) 

            # prints the address of the user that just connected 
            print(f'{addr[0]}: connected')

            # creates and individual thread for every user 
            # that connects 
            start_new_thread(self.clientthread,(client,))

class Client():
    """Since, we will need to send messages and login specifics clients
       we need a way to identify them """
    def __init__(self,addr,conn):
        self.addr = addr
        self.conn = conn
        self.client_id = None
        self.password = None

    def login(self,client_id,password):
        self.client_id = client_id
        self.password = password
        print(f"< Server > {self.addr[0]} logged as {self.client_id}")

    """Send message to client of this specific object"""
    def send(self,message):
        try: 
            self.conn.send(message.encode()) 
        except: 
            self.conn.close()
            raise Exception()
        
    def receive(self):
        message = self.conn.recv(2048) 
        return message.decode()



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