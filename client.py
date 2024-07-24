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
        self.list_of_commands = ['MSG','MSG_ALL','LOGIN','LOGOFF','LIST']
        print(f"Connected to Server {server_ip}:{server_port}")

    def validate_command(self,command):
        if command in self.list_of_commands:
            return True
        else:
            return False

    def parse_command(self,sentance):
        split_command = sentance.split(" ",1)
        if self.validate_command(split_command[0]):
            command = split_command[0]
            if command == 'MSG':
                body = split_command[1]
                split_body = body.split(" ",1)
                client_id = split_body[0]
                message = split_body[1]
                print(f'< You > < {client_id} > {message}')
            elif command == 'MSG_ALL':
                message = split_command[1]
                print(f'< You > {message}')
            elif command == 'LOGIN':
                body = split_command[1]
                split_body = body.split()
                client_id = split_body[0]
                print(f'< You > LOGIN {client_id}')
            elif command == 'LOGOFF':
                print('< You > LOGFF')
            elif command == 'LIST':
                print('< You > LIST')
            return True
        else:
            return False

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
                    if message != b'':
                        print (message.decode()) 
                else:
                    try: 
                        message = sys.stdin.readline() ## Reads message from stdin input 
                        if self.parse_command(message.rstrip('\n')):
                            self.server.send(message.encode()) ## send message to the server 
                        else: 
                            print("Invalid command")
                    except:
                        print("Fail to send message to server!!!")
                        continue

if len(sys.argv) != 3: 
    print ("Correct usage: script, IP address, port number")
    exit() 
IP_address = str(sys.argv[1]) 
Port = int(sys.argv[2]) 

client = Client(IP_address,Port)
client.start()
client.server.close()
