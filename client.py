import socket
import pickle    #to convert lists(any object) into bits format to send in transmission.
from multiprocessing import Process  #for multiprocessing on sending and recieving messages.
import sys

HEADER = 5084  #it tells the length of the amount of bytes we are going to recieve.
PORT = 5080   #computer port, usually above 4000 in unused, so we use 5050 for best circmstances.
SERVER = socket.gethostbyname(socket.gethostname())  # it creates a server at the IP give, in this case the IP is being extracted by the given code (IPV4- local address).
FORMAT = 'utf-8' #encoder
DISSCONNECT_MESSAGE = "!DISSCONNECT" #for disconnection, dissconnection msg.
ADDR = (SERVER, PORT)

def send_name(client, name):
    name = name.encode(FORMAT)
    name += b" " * (HEADER - len(name))
    client.send(name)   #send the name of the new client when they join to the server.

def send(client, msg):
    message = msg.encode(FORMAT)  #encodes the string in byte.
    msg_length = len(message)  #calculate the length
    send_length = str(msg_length).encode(FORMAT)  #ecode the length because we will send the length first.
    send_length += b' ' * (HEADER - len(send_length)) #b' ' will change the blank into byte format and add to the send_length to make it 64 byte long.
    client.send(send_length)   #sending the length first following the protocol.
    client.send(message)   #sending the message to the server.

    print("Me: " + msg)

def rec(client):   #for recieving messages.
    while True:   #process of recieving should be always checking for new messages.
        warning = client.recv(HEADER).decode(FORMAT)   #recieving the warning message.
        if not warning:  #checking if the warning is recieved to check for incomming messages.
            pass
        else:
            if warning.strip() == "new":     #checks if the new user is comming.
                new_client = (client.recv(HEADER).decode(FORMAT)).strip()   #decodes the name of the new client.
                print(f"[NEW USER]: {new_client} joined the chat.")

            elif warning.strip() == "joined":      #checks for the thw already connected client warning.
                already_connected = (client.recv(HEADER)).strip()    #takes the already connected client list in byte format.
                users_list = pickle.loads(already_connected)       #decodes the byte format back to list.
                if len(users_list) != 0:       #checks if there is any client or not.
                    print(",".join(users_list)+" already in the chat!")

            elif warning.strip() == "dissconnect":     #checks for dissconnection message warning.
                dissconnector_name = (client.recv(HEADER).decode(FORMAT).strip())     #recieves the dissconnected client's name.
                print(f"[DISSCONNECTION] {dissconnector_name} DISSCONNECTED!")

            else:
                msg_rec_len = warning       #if there is not warning then it must be the lenght of upcomming message.
                msg_rec_len = int(msg_rec_len)
                msg_rec = client.recv(msg_rec_len).decode(FORMAT)   #recieving the message itself.

                sender_name = client.recv(HEADER).decode(FORMAT)

                print(f"{sender_name}: {msg_rec}")


if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)   #connecting to the server.

    name = input("Enter Name: ")     #asks the name of the client.
    send_name(client, name)

    Process(target= rec, args= (client,)).start()  #multiprocessing
    while True:
        msg = input()
        Process(target = send, args=(client, msg,)).start()
        if msg == DISSCONNECT_MESSAGE:
            sys.exit()
