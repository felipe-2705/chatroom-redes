# Python program to implement client side of chat room.
# This is a modified version of https://www.geeksforgeeks.org/simple-chat-room-using-python/  
import socket 
import select 
import sys 


class Client():

    def __init__(self,server_ip, server_port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((server_ip, server_port))
        self.socket_list = [self.server, sys.stdin]
        print(f"Connected to Server {server_ip}:{server_port}")

    def start(self):
        while True: 
            """ There are two possible input situations. Either the 
            user wants to give manual input to send to other people, 
            or the server is sending a message to be printed on the 
            screen. Select returns from sockets_list, the stream that 
            is reader for input. So for example, if the server wants 
            to send a message, then the if condition will hold true 
            below.If the user wants to send a message, the else 
            condition will evaluate as true"""
            read_sockets,_, _ = select.select(self.socket_list,[],[]) 

            for socks in read_sockets: 
                if socks == self.server: 
                    message = socks.recv(2048) 
                    print (message) 
                else: 
                    message = sys.stdin.readline() ## Reads message from stdin input 
                    self.server.send(message) ## send message to the server 
                    sys.stdout.write("<You>") ## write message to your screen
                    sys.stdout.write(message) 
                    sys.stdout.flush() ## clean stdout

if len(sys.argv) != 3: 
    print ("Correct usage: script, IP address, port number")
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 

client = Client(IP_address,Port)
client.start()
client.server.close()
