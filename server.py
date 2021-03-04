import socket
import threading
import pickle

HEADER = 5084  #it tells the length of the amount of bytes we are going to recieve.
PORT = 5080   #computer port, usually above 4000 in unused, so we use 5050 for best circmstances.
SERVER = socket.gethostbyname(socket.gethostname())  # it creates a server at the IP give, in this case the IP is being extracted by the given code (IPV4- local address).
ADDR = (SERVER, PORT) # create a tuple
FORMAT = 'utf-8' #encoder
DISSCONNECT_MESSAGE = "!DISSCONNECT" #for disconnection, dissconnection msg.

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # server = socket.socket() is how we create a socket, we have to create a socket and combine it with the server. now inside that we define a family of socket which we want, which for IPV$ we use "socket.AF_INET" and "socket.SOCK_STREAM" is the type or method.
server.bind(ADDR) #here we bind the server(address) to the socket, i.e anything that connects to the address goes to the socket.

conn_list = {}  #connection list
conn_list_names = []   #list of names.

def handle_client(conn, addr):  # this part will handel the individual clients in the server.
    global conn_list
    print(f"[NEW CONNECTION] {addr} connected.")  #it tells us who connected.

    connected = True
    while connected:
        try:    #error handeling if someone close the window without sending the dissconnection message.
            msg_length = conn.recv(HEADER).decode(FORMAT) #here it decodes the msg length from byte format.
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode(FORMAT) #here it decodes the msg itself.
            if not msg:
                pass
            elif msg == DISSCONNECT_MESSAGE:    #checks for dissconnection.
                connected = False
                dissconnector_name = (conn_list[conn]).encode(FORMAT)    #takes out the disconnector's name.
                print(f"[DISSCONNECTION] {conn_list[conn]} dissconneced.")
                conn_list.pop(conn)    #removing the dissconnetor's name from the connection list.
                dissconnect_message = "dissconnect".encode(FORMAT)    #sending the warning for the dissconnnection message.
                dissconnect_message += b" " * (HEADER-len(dissconnect_message))

                dissconnector_name += b" " * (HEADER-len(dissconnector_name))
                for i in conn_list:
                    i.send(dissconnect_message)   #sending dissconnection warning to all the clients.
                    i.send(dissconnector_name)    #sending the dissconnnector's name to all the clients.

                pass
            else:
                print(f"[{addr}] [{conn_list[conn]}]: {msg}") #prints the msg with the sender address.

                message = msg.encode(FORMAT)
                message_length = len(message)
                message_length = str(message_length).encode(FORMAT)
                message_length += b' ' * (HEADER - len(message_length))  #converting the msg and its length as shown before in client side code.

                for i in conn_list:
                    if i == conn:
                        sender_name = conn_list[i]   #getting the sender name from the conn_list.

                for i in conn_list:
                    if i != conn:
                        i.sendall(message_length)  
                        i.sendall(message)   #sending messages to all the connections(clients) available accept the sender.
                        i.sendall(sender_name.encode(FORMAT))     #sending the name of sender.
        except ConnectionResetError:    #if error happens, which happens in the case when someone closes the window without sending the dissconnection message.
            connected = False    #so that loop ends.
            try:        #error handling when someone dissconnects whithout entering name.
                dissconnector_name = (conn_list[conn]).encode(FORMAT)    #takes out the disconnector's name.
                print(f"[DISSCONNECTION] {dissconnector_name.decode(FORMAT)} DISSCONECTED WITHOUT INFORMING!")
                conn_list.pop(conn)       #removing the dissconnetor's name from the connection list.
                dissconnect_message = "dissconnect".encode(FORMAT)      #sending the warning for the dissconnnection message.
                dissconnect_message += b" " * (HEADER-len(dissconnect_message))

                dissconnector_name += b" " * (HEADER-len(dissconnector_name))
                for i in conn_list:
                    i.send(dissconnect_message)      #sending dissconnection warning to all the clients.
                    i.send(dissconnector_name)       #sending the dissconnnector's name to all the clients.
                pass
            except KeyError:    #error handling when someone dissconnects whithout entering name.
                print("[DISSCONNECTION] Someone dissconnected without entering name.")

    conn.close()  #closes connection.
    
def start():  #it will start the socket server.    Also this part is only responsible for new connections.
    global conn_list
    global conn_list_names
    server.listen()  #listening for new connections.
    print(f"[LISTENING] Server is listening on {SERVER}")  #print the IP address of the server.

    while True:    #infinite loop till we turn it off
        conn, addr = server.accept()  #here the program will wait for the new connection, and when a connection is made it will store the address, and an object(conn) which will help us to transfer the data back to that connection.
        
        thread = threading.Thread(target=handle_client, args=(conn, addr))  # threading syntax in pyhton 3.
        thread.start()

        try:      #error handling when someone dissconnects whithout entering name.
            name = conn.recv(HEADER)  #recieving the name of the client, no need to fit into header size beacuse it was already done at client side.
        
            new_user_warning = "new".encode(FORMAT)         #encoding the new user warning.
            new_user_warning += b" " * (HEADER-len(new_user_warning))
            for i in conn_list:
                    i.send(new_user_warning)    #sending a code first to tell the client that its a new client is connected.
                    i.send(name)     #sending the name of client if someone joined the chat.

            for i in conn_list:
                conn_list_names.append(conn_list[i])   #making a list of only names if clients.
            conn_list_names_byte = pickle.dumps(conn_list_names)
            conn_list_names_byte += b" " * (HEADER - len(conn_list_names_byte))     #changing it into a byte format using pickle.

            connected_user_warning = "joined".encode(FORMAT)
            connected_user_warning += b" " * (HEADER - len(connected_user_warning))     

            conn.send(connected_user_warning)     
            conn.send(conn_list_names_byte)      #sending the names of already connected users.

            conn_list_names = []

            conn_list[conn] = (name.decode(FORMAT)).strip()    #adding any new connectons to the connection list.

            print(f"[ACTIVE CONNECTIONS] {threading.activeCount() - 1} : {(name.decode(FORMAT)).strip()} JIONED THE CHAT")  #it tells the number of active connections running, (-1) because one thread (start) is always running.

        except ConnectionResetError:                 #error handling when someone dissconnects whithout entering name.
            pass


print("[STARTING] server is starting....")
start()