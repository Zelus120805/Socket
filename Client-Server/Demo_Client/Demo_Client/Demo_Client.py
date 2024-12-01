import socket
import os
import time 
import sys
header = 64
formatMsg = 'utf-8'

serverPort = 12000
serverIP = '192.168.0.101'

client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = (serverIP,serverPort)

client.connect(addr)
def download_file():
    pass
  
def client_login():
    userName = input("Input your username: ")
    password = input("Input your password: ")
    if userName and password:
        sendMessage(userName)
        sendMessage(password)
        res = client.recv(1).decode(formatMsg)
        print(res)
        if res=='1':
            return True, userName
        else:
            return False, userName
    else:
        print("Invalid input. Please input again!")
        return False, userName
    
def upload_file(filePath):
    fin = open(filePath,"rb")
    
    sizeOfFile = os.path.getsize(filePath)#Lấy kích thước file
    totalBytes = 0 #Tính toán tổng số bytes
    startTime = time.time() #Thời điểm bắt đầu
    while totalBytes < sizeOfFile:
        data = fin.read(1024)# Mỗi lần đọc tối đa 1Mb
        if not data:
             break
        
        finLength = len(data)
        sendLength = str(finLength).encode()
        sendLength += b' '*(header - len(sendLength))
        client.send(sendLength)
        client.send(data)
        
        totalBytes += len(data)
       
        duration = time.time() - startTime
        process = (totalBytes/sizeOfFile)*100
       
        if(duration > 0):
            speed = totalBytes/duration
            sys.stdout.write(f"\rSpeed: {speed:.2f} bytes/s")  # Hiển thị trên một dòng
            sys.stdout.flush()  # Cập nhật ngay lập tức
    #Tín hiệu kết thúc file
    sendLength = str(0).encode(formatMsg)
    sendLength += b' ' * (header - len(sendLength))
    client.send(sendLength)
    
    response = client.recv(2048).decode(formatMsg)
    print(f"\n[SERVER RESPONSE]:{response}")
    fin.close()


def sendMessage(msg):
    msgContent = msg.encode(formatMsg)
    msgLength = len(msgContent)
    sendLength = str(msgLength).encode(formatMsg)
    sendLength += b' '*(header - len(sendLength))
    client.send(sendLength)
    client.send(msgContent)
    

def main():
    isLogined = False
    while not isLogined:
        isLogined, userName = client_login()
        if isLogined:
            os.system('cls')
        while isLogined:
            print(f"Welcome {userName}^^")
            request = input()
            sendMessage(request)
            if ' ' in request:
                command, filePath = request.split(' ', maxsplit = 1)
                filePath = filePath[1:-1]
            else:
                command = request
            if command.strip().lower() == 'logout':
                isLogined = False
                break
            if command.strip().lower() == 'close':
                client.close()
                return
            elif command.strip().lower() == 'upload' and filePath:
                if os.path.exists(filePath) and not os.path.isdir(filePath):
                    upload_file(filePath)
main()