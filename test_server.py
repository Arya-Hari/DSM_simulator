import socket
import os
from _thread import *
from threading import *
import time

# files present in the server storage
files = {'file1':'','file2':'','file3':''}
clients = {}
page_tables = []
currently_reading = [0,0,0]
lock_for_currently_writing =[0,0,0]
waiting = []
flag = 0

ServerSocket = socket.socket()
host = '127.0.0.1'
port = 1233
ThreadCount = 0
try:
    ServerSocket.bind((host, port))
except socket.error as e:
    print(str(e))

print('Waiting for a Connection..')
ServerSocket.listen(5)


def threaded_client(connection,client_id):
    connection.send(str.encode('1Functionalities : read "filename" | write "filename" | stopread "filename"'))
    while True:

        reply = ""
        data = connection.recv(2048)
        from_client = data.decode('utf-8')

        # client closes connection 
        # exit the loop
        
        if from_client == 'exit':
            for i in page_tables:
                if i[0] == client_id:
                    print('Connection with client ',client_id,' closed')
                    filename = i[1]
                    if i[2] == "read":
                        currently_reading[int(filename[len(filename)-1])-1]-=1
                    page_tables[client_id-1][1] = "closed client"
                    page_tables[client_id-1][2] = ""
                    break
            connection.close()
            break

        # message from client
        from_client = from_client.split(" ")
        print("Request from client ",client_id," :",from_client)
        
        if len(from_client) != 2:
            print("Client ",client_id,' did not provide enough arguments')
            reply = "1Error : Invalid command. Please enter proper command"
            connection.send(str.encode(reply))
            continue

        # client wishes to read    
        if from_client[0] == 'read':
            # reading filename from client
            filename = from_client[1]
            global new_read
            new_read = "Yes"

            # checking if filename present in files or not
            if filename not in files:
                new_read = "No"
                print("Client ",client_id,' provided invalid filename to Read')
                reply = "1File not found! Enter valid filename"
                connection.send(str.encode(reply))

            else:
                # checking if client already has read access for current file
                if (page_tables[client_id-1])[1] == filename and (page_tables[client_id-1])[2] == "read":
                    new_read = "No"
                    print("Client ",client_id,' already has a read access')
                    reply = "1You already have the read access\nRead access only!!\nContents of "+filename+" are : \n***************************************************************\n"+files[filename]
                    connection.send(str.encode(reply))
                
                # checking if client has read access for another file
                elif (page_tables[client_id-1])[2] == "read":
                    new_read = "No"
                    print("Client ",client_id," already has a read access for : "+(page_tables[client_id-1])[1])
                    cur_filename = (page_tables[client_id-1])[1]
                    reply = "1You have the read access only for "+cur_filename+"\nRead access only!!\nContents of "+cur_filename+" are : \n***************************************************************\n"+files[cur_filename]
                    connection.send(str.encode(reply))

                # checking if page is writing to another file
                elif (page_tables[client_id-1])[1] != filename and (page_tables[client_id-1])[2] == "write":
                    new_read = "No"
                    print("Client ",client_id,' has a write access only for file ',filename)
                    reply = "1Access denied. You have write access for file "+filename
                    connection.send(str.encode(reply))
                
                # checking if required page is being written
                for i in page_tables:
                    if i[1] == filename and i[2] == "write":
                        new_read = "No"
                        # checking if current client is writing
                        if i[0] == client_id:
                            print("Client ",client_id,' has a write access for the file',filename)
                            reply = "1Access denied. You only have write access"
                            connection.send(str.encode(reply))
                        else: 
                            print("Client ",i[0],' is writing to the file')
                            reply = "1Access denied. Client "+str(i[0])+" is currently writing.\nWait until read access is granted? [Y/N]"
                            connection.send(str.encode(reply))
                            dataReadWait = connection.recv(2048)
                            from_client_read_wait = dataReadWait.decode('utf-8')
                            if from_client_read_wait != 'Y':
                                reply = "1...Aborting..."
                                connection.send(str.encode(reply))
                            else:
                                reply = "...Waiting..."
                                connection.send(str.encode(reply))
                                waiting.append(client_id)
                                print(waiting)
                                while(lock_for_currently_writing[int(filename[len(filename)-1])-1] != 0):
                                    pass
                                waiting.pop(0)
                                page_tables[client_id-1] = [client_id,filename,"read"]
                                currently_reading[int(filename[len(filename)-1])-1]+=1
                                print("Client ",client_id,' has been granted a read access')
                                reply = "1Read access granted\nContents of "+filename+" are : \n***************************************************************\n"+files[filename]
                                # Add file to reading list.
                                connection.send(str.encode(reply))
                    
                # file name is not currently being written and client does not have access
                if (new_read == "Yes"):
                    page_tables[client_id-1] = [client_id,filename,"read"]
                    currently_reading[int(filename[len(filename)-1])-1]+=1
                    print("Client ",client_id,' has been granted a Read access')
                    reply = "1Contents of "+filename+" are : \n***************************************************************\n"+files[filename]
                    # Add file to reading list.
                    connection.send(str.encode(reply))

        elif from_client[0] == 'stopread':
            # check if client is not currently reading
            if (page_tables[client_id-1])[2] == "write" or (page_tables[client_id-1])[2] == "":
                print("Client ",client_id,' has not been granted a read access')
                reply = "1Denied. You do not have read access and hence cannot stop"
                connection.send(str.encode(reply))
            else:
                filename = from_client[1]

                # checking if filename is valid
                if filename not in files:
                    print("Client ",client_id,' provided invalid filename to Read')
                    reply = "1File not found! Enter valid filename"
                    connection.send(str.encode(reply))
                
                # client has read access to some other file
                elif (page_tables[client_id-1])[1] != filename:
                    print("Client ",client_id,' does not have read access to ',filename)
                    reply = "1Denied. You do not have read access to filename "+filename+". You have read access to "+(page_tables[client_id-1])[1]
                    connection.send(str.encode(reply))
                
                # client has read access to current file
                else:
                    print("Client ",client_id,' read access revoked')
                    page_tables[client_id-1] = [client_id,filename,""]
                    currently_reading[int(filename[len(filename)-1])-1]-=1
                    reply = "1Reading stopped."
                    # Add file to reading list.
                    connection.send(str.encode(reply))

        elif from_client[0] == 'write':
            filename = from_client[1]
            global new_write
            new_write = "Yes"

            # checking if filename present in files or not
            if filename not in files:
                print("Client ",client_id,' provided invalid filename to write')
                reply = "1File not found! Enter valid filename"
                connection.send(str.encode(reply))
            
            else:
                # checking if client has a read access for any file
                if (page_tables[client_id-1])[2] == "read":
                    new_write = "No"
                    print("Client ",client_id," access denied. Client already has a read access for : "+(page_tables[client_id-1])[1])
                    cur_filename = (page_tables[client_id-1])[1]
                    reply = "1Access denied. You are reading "+cur_filename
                    connection.send(str.encode(reply))
                
                # checking if client has write access for a file
                elif (page_tables[client_id-1])[2] == "write":
                    new_write = "No"
                    # checking if write access is to current file
                    if (page_tables[client_id-1])[1] == filename:
                        print("Client ",client_id,' already has a write access')
                        reply = "1You already have the write access\nEnter what has to be written : "
                        connection.send(str.encode(reply))
                        from_client_to_write = (connection.recv(2048)).decode('utf-8')
                        updated_file = files[filename] +from_client_to_write+"."
                        files[filename] = updated_file 
                        reply = "1" + filename + " updated successfully\nDo you wish to continue writing? [Y/N] : "
                        connection.send(str.encode(reply))
                        dataWriteContinue = connection.recv(2048)
                        from_client_write_continue = dataWriteContinue.decode('utf-8')
                        if from_client_write_continue != 'Y':
                            reply = "1...Stopping write process..."
                            page_tables[client_id-1] = [client_id,filename,""]
                            lock_for_currently_writing[int(filename[len(filename)-1])-1] = 0
                            print("Client " + str(client_id) + " has revoked writing access")
                            connection.send(str.encode(reply))
                        else:
                            reply = "...Continuing..."
                            connection.send(str.encode(reply))
                    else:
                        print("Client ",client_id," access denied. Client has write access for : "+(page_tables[client_id-1])[1])
                        cur_filename = (page_tables[client_id-1])[1]
                        reply = "1Access denied. You are currently writing to "+cur_filename
                        connection.send(str.encode(reply))
                
                # checking if page is currently being read by another client
                elif currently_reading[int(filename[len(filename)-1])-1] != 0:
                    new_write = "No"
                    print("Client/s are reading the file")
                    reply = "1Access denied. Client/s are currently reading.\nWait until write access is granted? [Y/N]"
                    connection.send(str.encode(reply))
                    dataWriteWait = connection.recv(2048)
                    from_client_write_wait = dataWriteWait.decode('utf-8')
                    if from_client_write_wait != 'Y':
                        reply = "1...Aborting..."
                        connection.send(str.encode(reply))
                    else:
                        reply = "...Waiting..."
                        connection.send(str.encode(reply))
                        while(currently_reading[int(filename[len(filename)-1])-1] != 0):
                            pass
                        page_tables[client_id-1] = [client_id,filename,"write"]
                        lock_for_currently_writing[int(filename[len(filename)-1])-1] = 1
                        print("4Client ",client_id,' has been given write access')
                        reply = "1Access granted\nEnter what has to be written : "
                        connection.send(str.encode(reply))
                        from_client_to_write = (connection.recv(2048)).decode('utf-8')
                        updated_file = files[filename] +from_client_to_write+"."
                        files[filename] = updated_file 
                        reply = "1" + filename + " updated successfully\nDo you wish to continue writing? [Y/N] : "
                        connection.send(str.encode(reply))
                        dataWriteContinue = connection.recv(2048)
                        from_client_write_continue = dataWriteContinue.decode('utf-8')
                        if from_client_write_continue != 'Y':
                            reply = "1...Stopping write process..."
                            lock_for_currently_writing[int(filename[len(filename)-1])-1] = 0
                            page_tables[client_id-1] = [client_id,filename,""]
                            print("Client " + str(client_id) + " has revoked writing access")
                            connection.send(str.encode(reply))
                        else:
                            reply = "1...Continuing..."
                            connection.send(str.encode(reply))
                
                # checking if page is being written by another client
                # Not including read here as multiple clients can be reading the same file
                for i in page_tables:
                    if i[1] == filename and i[2] == "write" and i[0] != client_id:
                        new_write = "No"
                        print("Client ",i[0],' is writing to the file')
                        print(client_id)
                        reply = "1Access denied. Client "+str(i[0])+" is currently writing.\nWait until write access is granted? [Y/N]"
                        connection.send(str.encode(reply))
                        dataReadWait = connection.recv(2048)
                        from_client_read_wait = dataReadWait.decode('utf-8')
                        if from_client_read_wait != 'Y':
                            reply = "1...Aborting..."
                            connection.send(str.encode(reply))
                        else:
                            reply = "...Waiting..."
                            connection.send(str.encode(reply))
                            waiting.append(client_id)
                            while(lock_for_currently_writing[int(filename[len(filename)-1])-1] != 0):
                                pass
                            waiting.pop(0)
                            page_tables[client_id-1] = [client_id,filename,"write"]
                            lock_for_currently_writing[int(filename[len(filename)-1])-1] = 1
                            print("5Client ",client_id,' has been given write access')
                            reply = "1Access granted\nEnter what has to be written : "
                            connection.send(str.encode(reply))
                            from_client_to_write = (connection.recv(2048)).decode('utf-8')
                            updated_file = files[filename] +from_client_to_write+"."
                            files[filename] = updated_file 
                            reply = "1" + filename + " updated successfully\nDo you wish to continue writing? [Y/N] : "
                            connection.send(str.encode(reply))
                            dataWriteContinue = connection.recv(2048)
                            from_client_write_continue = dataWriteContinue.decode('utf-8')
                            if from_client_write_continue != 'Y':
                                reply = "1...Stopping write process..."
                                print("Client " + str(client_id) + " has revoked writing access")
                                lock_for_currently_writing[int(filename[len(filename)-1])-1] = 0
                                page_tables[client_id-1] = [client_id,filename,""]
                                connection.send(str.encode(reply))
                            else:
                                reply = "1...Continuing..."
                                connection.send(str.encode(reply))

                if (new_write == "Yes"):
                    page_tables[client_id-1] = [client_id,filename,"write"]
                    lock_for_currently_writing[int(filename[len(filename)-1])-1] = 1
                    print("6Client ",client_id,' has been given write access')
                    reply = "1Access granted\nEnter what has to be written : "
                    connection.send(str.encode(reply))
                    from_client_to_write = (connection.recv(2048)).decode('utf-8')
                    updated_file = files[filename] +from_client_to_write+"."
                    files[filename] = updated_file 
                    reply = "1" + filename + " updated successfully\nDo you wish to continue writing? [Y/N] : "
                    connection.send(str.encode(reply))
                    dataWriteContinue = connection.recv(2048)
                    from_client_write_continue = dataWriteContinue.decode('utf-8')
                    if from_client_write_continue != 'Y':                                
                        reply = "1...Stopping write process..."
                        page_tables[client_id-1] = [client_id,filename,""]
                        lock_for_currently_writing[int(filename[len(filename)-1])-1] = 0
                        print("Client " + str(client_id) + " has revoked writing access")
                        connection.send(str.encode(reply))
                    else:
                        reply = "1...Continuing..."
                        connection.send(str.encode(reply))
        # Command not indentified by the 
        else :
            print("Invalid command from Client ",client_id)
            reply = "1Enter valid command"
            connection.send(str.encode(reply))

while True:

    Client, address = ServerSocket.accept()
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    page_tables.append([ThreadCount+1,"",""])
    print(page_tables)
    start_new_thread(threaded_client, (Client,  ThreadCount+1))
    ThreadCount += 1
    print('Client Number: ' + str(ThreadCount))
ServerSocket.close()