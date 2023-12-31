import socket
import zlib
from src import *
import sys


'''
Network features for local area network
'''


class Server:
    def __init__(self,port:int,connection_timeout:int = 2,compress_messages:bool=True):#constructor
        self.socket_ = socket.socket()  # create socket object
        self.port_ = port
        self.error_message_ = ""

        self.compress_messages_ = compress_messages #compress sent message and decompress incoming messages


        self.socket_.settimeout(connection_timeout)
        self.connected_ = False

        self.message_sended_this_loop_round_ = False  #send some message every loop round

        try:
            self.socket_.bind(('', port)) #bind socket
            print("socket binded to %s" % (port))
            self.socket_.listen(1) #Listen for incoming connections
            print("socket is listening")

            try:
                self.client_, self.addr_ = self.socket_.accept()  # waiting for someone to connect
                self.connected_ = True
                self.client_.settimeout(1)
            except Exception as message:
                self.error_message_ = str(message)
                self.connected_ = False

        except Exception as message:
            self.error_message_ = str(message)


        self.__buffer = [] #private method, received messages
        #buffer = [[data_type,data],[data_type,data]]



        #data_type_: "map","readytostart","gameexit","restartlevel",None,action, "other"

        #data_:
        #map = str
        #action = str
        #points:int
        #points_collected_ = int
        #readytostart = tuple, (join id,program version)
        #gameexit = None
        #restartlevel = None
        #other = str
        #None = None


    def SetTimeout(self,timeout)->None:
        self.client_.settimeout(timeout)  # set new timeout

    def Read(self)->None:
        #read socket message to buffer


        try:

            messages = self.client_.recv(10000) #read messages
            if self.compress_messages_ == True:
                messages = zlib.decompress(messages).decode()  # decompress and decode
            else:
                messages = messages.decode()  # only decode

            messages = messages.split(";") #split messages to list


            for message in messages:
                if len(message) == 0: #if no message or message is empty
                    pass
                else:
                    # exmine message data type and set data
                    if message[0:7] == "action:":
                        self.__buffer.append(["action",message[7:]])

                    elif message[0:6] == "ingoal":
                        self.__buffer.append(["ingoal", None])

                    elif message[0:4] == "map:":  # if message is map
                        self.__buffer.append(["map",message[4:]])

                    elif message[0:13] == "readytostart:": #if message is "readytostart"
                        self.__buffer.append(["readytostart",(message[13:18],message[18:])])

                    elif message[0:9] == "gameexit":  # if message is gameexit
                        self.__buffer.append(["gameexit",None])

                    elif message[0:13] == "restartlevel":
                        self.__buffer.append(["restartlevel",None])


        except: #connection failed
            self.connected_ = False





    @property
    def data_type_(self)->str:
        '''
        return data type of the first message in the buffer
        '''
        if len(self.__buffer) == 0: #if buffer is empty
            return None
        else:
            return self.__buffer[0][0] #retrun str

    @property
    def data_(self):
        '''
        return first message from buffer
        '''
        if len(self.__buffer) == 0: #if buffer is empty
            return(None)
        else:
            return self.__buffer[0][1]


    def BufferNext(self)->None:
        '''
        delete first message from buffer
        '''

        if len(self.__buffer) > 0: #if buffer is no empty
            self.__buffer.pop(0)



    def __SendMessage(self, message:str)->None:  # private method

        message += ";"

        if self.compress_messages_ == True:
            message = zlib.compress(message.encode())  #compress and send message
        else:
            message = message.encode()  #send message without compress

        try:
            self.client_.send(message) #send message
            self.message_sended_this_loop_round_ = True
        except: #if connection lost
            self.connected_ = False


    def SendPass(self):
        '''
        send "pass;" message
        '''

        message = "pass"
        self.__SendMessage(message)



    def SendMap(self,mapstr:str)->None:
        #send full map

        maplist = mapstr.split(",") #convert str to list

        find_1 = maplist.index("1") #find local player position
        find_2 = maplist.index("2") #find remoteplayer position

        #change local player --> remote player
        #and remote player --> local player
        maplist[find_1] = "2"
        maplist[find_2] = "1"


        mapstr = ",".join(maplist) #connvert list to str

        message = f"map:{mapstr}"
        self.__SendMessage(message) #send message


    def SendMove(self,right:bool,left:bool,up:bool,down:bool,door:bool=False)->None:
        '''
        send action:
        a player's moves
        '''

        if right == True:
            message = f"action:moveright:{int(door)}"
        elif down == True:
            message = f"action:movedown:{int(door)}"
        elif left == True:
            message = f"action:moveleft:{int(door)}"
        elif up == True:
            message = f"action:moveup:{int(door)}"

        self.__SendMessage(message) #send message


    def SendPush(self,right:bool,left:bool)->None:
        '''
        send action:
        push object
        '''
        if right == True:
            message = "action:pushright"
        elif left == True:
            message = "action:pushleft"

        self.__SendMessage(message) #send message


    def SendRemove(self,right:bool,left:bool,up:bool,down:bool)->None:
        '''
        send  action:
        remove next to player
        '''
        if right == True:
            message = "action:removeright"
        elif down == True:
            message = "action:removedown"
        elif left == True:
            message = "action:removeleft"
        elif up == True:
            message = "action:removeup"

        self.__SendMessage(message) #send message




    def SendStartInfo(self,map_height:int,map_width:int,required_score:int=0,timelimit:int = 0)->None:
        '''
        a message about the start of the game
        send map size y,z and required_score
        '''

        message = f"startinfo:{str(map_height)},{str(map_width)},{str(required_score)},{str(timelimit)}"

        self.__SendMessage(message) #send message


    def SendWrongVersion(self):
        #send wrong version message
        message = "wrongversion"
        self.__SendMessage(message)

    def SendInGoal(self):
        message = "ingoal"

        self.__SendMessage(message)

    def SendGameExit(self): #if game exit
        message = "gameexit"
        self.__SendMessage(message) #send message

    def SendRestartLevel(self)->None:
        message = "restartlevel"
        self.__SendMessage(message) #send message

    def CloseSocket(self)->None:
        self.socket_.close()





class Client:
    def __init__(self,ipaddress:str,port:int,compress_messages:bool=True):
        self.socket_ = socket.socket()  # create socket object
        self.socket_.settimeout(5)
        self.ipaddress_ = ipaddress
        self.port_ = port

        self.connected_ = False
        self.error_message_ = ""

        self.compress_messages_ = compress_messages #compress sent message and decompress incoming messages

        self.message_sended_this_loop_round_ = False #send some message every loop round


        try: #try connect to server
            self.socket_.connect((ipaddress, port))
            self.connected_ = True
            self.socket_.settimeout(1)
        except Exception as message:
            self.error_message_ = str(message)
            self.connected_ = False


        self.__buffer = [] #private method, received messages
        #buffer = [[data_type,data],[data_type,data]]

        #data_type_: "map","startinfo","gameexit","restartlevel",None,action, "other"

        #data_:
        #map = str
        #startinfo = tuple (map_height,map_width)
        #wrongversion = None
        #gameexit = bool
        #restartlevel = None
        #other = str
        #None = None


    def SetTimeout(self,timeout)->None:
        self.socket_.settimeout(timeout)  # set new timeout


    def Read(self)->None:
        #read socket message


        try:

            messages = self.socket_.recv(10000) #read socket

            if self.compress_messages_ == True:
                messages = zlib.decompress(messages).decode() #decompress and decode
            else:
                messages = messages.decode() #only decode


            messages = messages.split(";")  # split messages to list

            for message in messages:

                if message[0:7] == "action:":
                    self.__buffer.append(["action",message[7:]])

                elif message[0:6] == "ingoal":
                    self.__buffer.append(["ingoal", None])

                elif message[0:4] == "map:":  # if message is map
                    self.__buffer.append(["map",message[4:]])


                elif message[0:10] == "startinfo:": #if message is startinfo
                    datalist = message[10:].split(',') #split str to list
                    map_height = int(datalist[0])  #map size y
                    map_width = int(datalist[1])  #map size x
                    required_score = int(datalist[2]) #required_score
                    timelimit = int(datalist[3]) #timelimit

                    self.__buffer.append(["startinfo",(map_height,map_width,required_score,timelimit)])

                elif message[0:13] == "wrongversion":
                    self.__buffer.append(["wrongversion",None])

                elif message[0:8] == "gameexit": #if message is gameexit
                    self.__buffer.append(["gameexit",None])

                elif message[0:13] == "restartlevel":
                    self.__buffer.append(["restartlevel",None])


        except Exception as error_message: #connection failed
            self.error_message_ = str(error_message)
            self.connected_ = False




    @property
    def data_type_(self)->str:
        '''
        return data type of the first message in the buffer
        '''
        if len(self.__buffer) == 0: #if buffer is empty
            return None
        else:
            return self.__buffer[0][0] #retrun str

    @property
    def data_(self)->str:
        '''
        return first message from buffer
        '''
        if len(self.__buffer) == 0: #if buffer is empty
            return(None)
        else:
            return self.__buffer[0][1]


    def BufferNext(self)->None:
        '''
        delete first message from buffer
        '''

        if len(self.__buffer) > 0: #if buffer is no empty
            self.__buffer.pop(0)



    def __SendMessage(self,message:str)->None: #private method

        message += ";"

        if self.compress_messages_ == True:
            message = zlib.compress(message.encode())  # compress and send message
        else:
            message = message.encode()  #send message without compress

        try:
            self.socket_.send(message) #send message
        except: #if connection lost
            self.connected_ = False

        self.message_sended_this_loop_round_ = True


    def SendPass(self):
        '''
        send "pass;" message
        '''

        message = "pass"
        self.__SendMessage(message)


    def SendReadyToStart(self,check_number:str,program_version:str)->None:
        message = f"readytostart:{check_number}{program_version}"

        self.__SendMessage(message) #send message


    def SendMove(self,right:bool,left:bool,up:bool,down:bool,door:bool=False)->None:
        '''
        send action:
        a player's moves
        '''

        if right == True:
            message = f"action:moveright:{int(door)}"
        elif down == True:
            message = f"action:movedown:{int(door)}"
        elif left == True:
            message = f"action:moveleft:{int(door)}"
        elif up == True:
            message = f"action:moveup:{int(door)}"

        self.__SendMessage(message)  # send message
    def SendPush(self,right:bool,left:bool):
        '''
        send action:
        push object
        '''

        if right == True:
            message = "action:pushright"
        elif left == True:
            message = "action:pushleft"

        self.__SendMessage(message)  # send message

    def SendRemove(self,right:bool,left:bool,up:bool,down:bool)->None:
        '''
        send action:
        remove next to player
        '''

        if right == True:
            message = "action:removeright"
        elif down == True:
            message = "action:removedown"
        elif left == True:
            message = "action:removeleft"
        elif up == True:
            message = "action:removeup"

        self.__SendMessage(message)  # send message


    def SendInGoal(self):
        message = "ingoal"

        self.__SendMessage(message)


    def SendGameExit(self)->None: #if game exit
        message = "gameexit"

        self.__SendMessage(message)  # send message


    def SendRestartLevel(self)->None:
        message = "restartlevel"
        self.__SendMessage(message)  # send message


    def CloseSocket(self)->None:
        self.socket_.close()