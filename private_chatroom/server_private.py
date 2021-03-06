import socket
import threading

HEADER = 5084  #it tells the length of the amount of bytes we are going to recieve.
PORT = 5050   #computer port, usually above 4000 in unused, so we use 5050 for best circmstances.
SERVER = socket.gethostbyname(socket.gethostname())  # it creates a server at the IP give, in this case the IP is being extracted by the given code (IPV4- local address).
ADDR = (SERVER, PORT) # create a tuple
FORMAT = 'utf-8' #encoder
DISSCONNECT_MESSAGE = "!DISSCONNECT" #for disconnection, dissconnection msg.

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server = socket.socket() is how we create a socket, we have to create a socket and combine it with the server. now inside that we define a family of socket which we want, which for IPV$ we use "socket.AF_INET" and "socket.SOCK_STREAM" is the type or method.
server.bind(ADDR) #here we bind the server(address) to the socket, i.e anything that connects to the address goes to the socket.

conn_list = {}  #connection list.
chat_list = {}  #chatroom list(contains the name of users in the chat room).


def invite(conn, name):
    global conn_list
    global chat_list
    global friend_conn
    friend = conn.recv(HEADER)  #recieving friend's name.
    friend = (friend.decode(FORMAT)).strip()

    try:
        connection_msg = "connected"
        if friend == (name.decode(FORMAT)).strip():     #so that no one enters there own name in friend's name.
            same_name = "same_name".encode(FORMAT)
            same_name += b" " * (HEADER-len(same_name))
            conn.send(same_name)    #sending client a warning that they have enter their own name.
            invite(conn, name)      #starting the fuction again to recieve friend's name.
            return
        len_conn_list = 0
        for i in conn_list:
            len_conn_list += 1
            if conn_list[i] == friend:  #searching if the entered friend's name is connected or not.
                len_conn_list = 0
                friend_conn = i
                connection_msg = "connected"    #if the name entered is connected to the server 'connected' msg will be sent.
        if len_conn_list == len(conn_list):     #this means that the name entered is not found in the list i.e. friend is not connected to the server.
            not_found_msg = "not_found".encode(FORMAT)  #in this case 'not_found' will be transmitted.
            not_found_msg += b" " * (HEADER-len(not_found_msg))
            conn.send(not_found_msg)    #the not_found msg is transmitted.
            invite(conn, name)      #as its not found the invite function is called again and the whole process of asking friend's name is started again.
            return
        else:
            found_msg = "found".encode(FORMAT)
            found_msg += b" " * (HEADER-len(found_msg))
            conn.send(found_msg)    #here found msg is trans mitted to the client.

        chat_list[conn] = [(conn, (name.decode(FORMAT)).strip()), (friend_conn, friend)]    #once connected connection details of client and their friend is being added to the chat_list.
        chat_list[friend_conn] = [(friend_conn, friend), (conn, (name.decode(FORMAT)).strip())]     #continued... it contains {connection_address_client:[(connection_address_client, client_name),(connection_address_friend,friend_name)]}

        connection_msg = connection_msg.encode(FORMAT)
        connection_msg += b" " * (HEADER - len(connection_msg))
        friend_conn.send(connection_msg)    #telling the client and their friend that a have been connected by sending them 'connected' message.
        conn.send(connection_msg)
        print(f"[ROOM CREATED] with {(name.decode(FORMAT)).strip()} and {friend}.") #prints that a room have been created between the client and their friend.
    except RuntimeError:
        pass
    except ConnectionResetError:
        pass

def handle_client(conn, addr, name):  # this part will handel the individual clients in the server.
    global conn_list
    global chat_list
    global friend_conn
    print(f"[NEW CONNECTION] {addr} connected.")  #it tells us who connected.

    connected = True
    while connected:
        try:    #error handeling if someone close the window without sending the dissconnection message.
            msg_length = (conn.recv(HEADER).decode(FORMAT)).strip() #here it decodes the msg length from byte format recied from the client.
            if not msg_length: #if no message is recieved then do nothing.
                pass
            else:
                if msg_length == "!invite": #if the message recieved is !invite then initiate the invite functioon.
                    invite(conn, name)

                elif msg_length == "!invited": #if message recieved is !invited then do nothing.
                    pass

                else:
                    msg_length = int(msg_length)
                    msg = conn.recv(msg_length).decode(FORMAT) #here it decodes the msg itself.
                    if not msg:
                        pass
                    elif msg.strip() == DISSCONNECT_MESSAGE:    #if its the dissconnect message then:.
                        print(f"[DISSCONNECTION] Chat ended between {(name.decode(FORMAT)).strip()} and {chat_list[conn][1][1]}.")
                        dissconnect_message = "dissconnect".encode(FORMAT)
                        dissconnect_message += b" " * (HEADER-len(dissconnect_message))

                        friend_conn = chat_list[conn][1][0]     #gets freind's connection address from the chat_list.
                    
                        chat_list[conn][1][0].send(dissconnect_message)  #sends the client the dissconnection message,
                        chat_list[conn][1][0].send(name)    #and name of the client who dissconnected.
                        conn_list.pop(conn) #removing the names of client and their friend from the conn_list and chat_list.
                        conn_list.pop(friend_conn)
                        chat_list.pop(conn)
                        chat_list.pop(friend_conn)
                        quit()  #ending the thread here.
                        pass
                    else:   #if the message is just normal chat.
                        try:
                            print(f"[{addr}] [{conn_list[conn]}] to [{chat_list[conn][1][1]}]: {msg}") #prints the msg with the sender address.

                            message = msg.encode(FORMAT)
                            message_length = len(message)
                            message_length = str(message_length).encode(FORMAT)
                            message_length += b' ' * (HEADER - len(message_length))  #converting the msg and its length as shown before in client side code.

                            sender_name = conn_list[conn]   #getting the sender name from the conn_list.

                            chat_list[conn][1][0].send(message_length)  
                            chat_list[conn][1][0].send(message)   #sending messages to all the connections(clients) available accept the sender.
                            chat_list[conn][1][0].send(sender_name.encode(FORMAT))     #sending the name of sender.
                        except KeyError:
                            pass

        except ConnectionResetError:    #if error happens, which happens in the case when someone closes the window without sending the dissconnection message.
            connected = False    #so that loop ends.
            try:        #error handling when someone dissconnects whithout entering name.
                print(f"[DISSCONNECTION] Chat ended between {chat_list[conn][0][1]} and {chat_list[conn][1][1]}.")  #prints that the chat between client and their friend is ended.
                dissconnect_message = "dissconnect".encode(FORMAT)      #sending the warning for the dissconnnection message.
                dissconnect_message += b" " * (HEADER-len(dissconnect_message))

                friend_conn = chat_list[conn][1][0]
                    
                chat_list[conn][1][0].send(dissconnect_message)    #sends the client the dissconnection message,
                chat_list[conn][1][0].send(name)    #and name of the client who dissconnected.
                conn_list.pop(conn)     #removing the names of client and their friend from the conn_list and chat_list.
                conn_list.pop(friend_conn)
                chat_list.pop(conn)
                chat_list.pop(friend_conn)
                quit()      #ending the thread here.
                return
            except KeyError:    #error handling when someone dissconnects whithout entering friend's name.
                print(f"[DISSCONNECTION] {conn_list[conn]} dissconnected without entering friend's name.")
                conn_list.pop(conn)     #removes the client name from the conn_list.

    conn.close()  #closes connection.

def accept_name(conn, addr):
    global conn_list
    name = conn.recv(HEADER)  #recieving the name of the client, no need to fit into header size beacuse it was already done at client side.

    len_conn_list = 0
    try:
        for i in conn_list:
            len_conn_list += 1
            if conn_list[i] == (name.strip()).decode(FORMAT):       #checks if the name entered already exists or not.
                name_confirmation = "no".encode(FORMAT)     #if yes the a a 'no' confirmation message is sent to the client.
                name_confirmation += b" " * (HEADER-len(name_confirmation))
                conn.send(name_confirmation)
                accept_name(conn, addr)     #the accept_name function is called to ask a different name this time. 
                return
        if len_conn_list == len(conn_list):     #if not then a 'yes' confirmation message is sent.
            name_confirmation = "yes".encode(FORMAT)
            name_confirmation += b" " * (HEADER-len(name_confirmation))
            conn.send(name_confirmation)
    except RuntimeError:
        pass

    conn_list[conn] = (name.decode(FORMAT)).strip()    #adding any new connectons to the connection list.

    thread = threading.Thread(target=handle_client, args=(conn, addr, name))  # threading syntax in pyhton 3.
    thread.start()

    print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1} : {(name.decode(FORMAT)).strip()} JIONED THE CHAT")  #it tells the number of active connections running, (-1) because one thread (start) is always running.

    
def start():  #it will start the socket server.    Also this part is only responsible for new connections.
    global conn_list
    global chat_list
    server.listen()  #listening for new connections.
    print(f"[LISTENING] Server is listening on {SERVER}")  #print the IP address of the server.

    while True:    #infinite loop till we turn it off
        conn, addr = server.accept()  #here the program will wait for the new connection, and when a connection is made it will store the address, and an object(conn) which will help us to transfer the data back to that connection.

        try:      #error handling when someone dissconnects whithout entering name.
            accept_name(conn, addr)

        except ConnectionResetError:                 #error handling when someone dissconnects whithout entering name.
            pass


print("[STARTING] server is starting....")
start()
