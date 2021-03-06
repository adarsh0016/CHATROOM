import socket
from multiprocessing import Process  #for multiprocessing on sending and recieving messages.
import sys

HEADER = 5084  #it tells the length of the amount of bytes we are going to recieve.
PORT = 5050   #computer port, usually above 4000 in unused, so we use 5050 for best circmstances.
SERVER = socket.gethostbyname(socket.gethostname())  # it creates a server at the IP give, in this case the IP is being extracted by the given code (IPV4- local address).
FORMAT = 'utf-8' #encoder
DISSCONNECT_MESSAGE = "!DISSCONNECT" #for disconnection, dissconnection msg.
ADDR = (SERVER, PORT)
CONNECTED = False

def send_friend(client):    #this fuction sends the friend's name to the server.
    friend = input("Enter Friend's Name: ")    #asks for friend's name to whom the client wants to be connected to.
    friend = friend.encode(FORMAT)
    friend += b" " * (HEADER - len(friend))
    client.send(friend)     #send the friend's name to the server.
    friend_confirmation = (client.recv(HEADER)).decode(FORMAT)      #recieves a confirmation that if the friend whit the entered name is connected to the server or not.
    friend_confirmation = friend_confirmation.strip()
    if friend_confirmation == "not_found":      #if the recieved confirmation is 'not_found' then starts the send_friend fuction again.
        print(f"There's no user with the name '{(friend.decode(FORMAT)).strip()}', check the name or tell your friend to connect first!")
        send_friend(client)
        pass
    elif friend_confirmation == "same_name":        #if the friend name is same as the client's name then also the send_friend fuction is called.
        print(f"You entered your own name!")
        send_friend(client)
        pass
    elif friend_confirmation == "found":        #is the recieved message is found, then we let it go on.
        pass

def send_name(client, name):    #this function sends the client's name to the server.
    name = name.encode(FORMAT)
    name += b" " * (HEADER - len(name))
    client.send(name)   #send the name of the new client when they join to the server.
    name_confirmation = (client.recv(HEADER)).decode(FORMAT)        #receives a confirmation message if the name entered already exists or not.
    name_confirmation = name_confirmation.strip()
    if name_confirmation == "no":       #if the message received is 'no' then the start fuction is called.
        print("This name already exists, try entering another name!")
        start(client)
        pass

def send(client, msg):
    message = msg.encode(FORMAT)  #encodes the string in byte.
    msg_length = len(message)  #calculate the length
    send_length = str(msg_length).encode(FORMAT)  #ecode the length because we will send the length first.
    send_length += b' ' * (HEADER - len(send_length)) #b' ' will change the blank into byte format and add to the send_length to make it 64 byte long.
    client.send(send_length)   #sending the length first following the protocol.
    client.send(message)   #sending the message to the server.

    if msg != DISSCONNECT_MESSAGE:
        print("Me: " + msg)     #prints the message entered
    else:
        print("DISSCONNECTED FROM THE CHAT!")
        return

def rec(client):   #for recieving messages.
    while True:   #process of recieving should be always checking for new messages.
        warning = client.recv(HEADER).decode(FORMAT)   #recieving the warning message.
        if not warning:  #checking if the warning is recieved to check for incomming messages.
            pass
        else:
            if warning.strip() == "connected":      #if the warning is 'connected' then prints connected.
                print("Freind connected!")
                return
            elif warning.strip() == "dissconnect":      #if the warning is dissconnected prints dissconnected with the name of the clinet who dissconnected.
                dissconnector_name = (client.recv(HEADER)).decode(FORMAT)
                dissconnector_name = dissconnector_name.strip()
                print(f"{dissconnector_name} was dissconnected!")
                return

            else:
                msg_rec_len = warning       #if there is not warning then it must be the lenght of upcomming message.
                msg_rec_len = int(msg_rec_len)
                msg_rec = client.recv(msg_rec_len).decode(FORMAT)   #recieving the message itself.

                sender_name = client.recv(HEADER).decode(FORMAT)

                print(f"{sender_name}: {msg_rec}")

def invitation(client):     #this fuction deals with the invitation of clients into the chat.
    correct = True
    while correct:
        command = input("Enter Command ('!invite' to invite your friend, or '!invited' if your friend is inviting you: ")       #asks if the client wants to invie or is being invited to the chat.
        command_trans = command.encode(FORMAT)
        command_trans += b" " * (HEADER - len(command_trans))

        if command == "!invite":        #if the client wants to invite, then it informs the server and calls the send_friend and rec functions.
            client.send(command_trans)
            send_friend(client)
            rec(client)
            correct = False
        elif command == "!invited":     #if the client wants ti be invited, then it informs the server and starts the rec fuction.
            client.send(command_trans)
            rec(client)
            correct = False
        else:
            print("Wrong command!")

def start(client):
    name = input("Enter Name: ")     #asks the name of the client.
    send_name(client, name)
    invitation(client)

    Process(target= rec, args= (client,)).start()  #multiprocessing.

    while True:
        msg = input()
        Process(target = send, args=(client, msg,)).start()     #multiprocessing.

if __name__ == '__main__':
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)   #connecting to the server.
    except ConnectionRefusedError:
        print("SERVER DOWN, try after some time.")
        sys.exit()

    start(client)
