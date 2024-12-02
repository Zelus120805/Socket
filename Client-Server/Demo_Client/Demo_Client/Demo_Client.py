import socket
import os
import time 
import sys
header = 64
formatMsg = 'utf-8'

serverPort = 65432
serverIP = '192.168.136.167'

client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = (serverIP,serverPort)

client.connect(addr)
def download_file():
    pass
  
def client_login():
    userName = input("Input your username: ")
    password = input("Input your password: ")
    if userName and password:
        send_message(userName)
        send_message(password)
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
        data = fin.read(500)# Mỗi lần đọc tối đa 1Mb
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
       
        if duration > 0:
            speed = totalBytes/duration
            sys.stdout.write(f"\rProcess: {process:.2f}%")  # Hiển thị trên một dòng
            sys.stdout.flush()  # Cập nhật ngay lập tức
 
    #Tín hiệu kết thúc file
    sendLength = str(0).encode(formatMsg)
    sendLength += b' ' * (header - len(sendLength))
    client.send(sendLength)
    
    response = client.recv(2048).decode(formatMsg)
    print(f"\n[SERVER RESPONSE]:{response}")
    fin.close()
def receive_message():
    msgLength = int(client.recv(header).decode(formatMsg))
    msgContent = client.recv(msgLength).decode(formatMsg)
    return msgContent

def send_message(msg):
    msgContent = msg.encode(formatMsg)
    msgLength = len(msgContent) 
    sendLength = str(msgLength).encode(formatMsg)
    sendLength += b' '*(header - len(sendLength))
    client.send(sendLength)
    client.send(msgContent)

#Hàm chuẩn hóa lệnh nhập (cmd)


def main():
    isLogined = False
    while not isLogined:
        isLogined, userName = client_login()
        if isLogined:
            os.system('cls')
            print(f"Welcome {userName}^^")
        while isLogined:
            request = input()
            send_message(request)
            if ' ' in request:
                command, filePath = request.split(' ', maxsplit = 1)
                filePath = filePath[1:-1]
            else:
                command = request
                filePath = ''
            if command.strip().lower() == 'logout':
                isLogined = False
                break
            if command.strip().lower() == 'close':
                client.close()
                return
            elif command.strip().lower() == 'upload' and filePath:
                if os.path.exists(filePath) and not os.path.isdir(filePath):
                    upload_file(filePath)
            elif command.strip().lower()=='view':
                #Nhận list file, mà đầu tiên là số file hiện có
                print("List available file")
                numOfFile = int(receive_message())
                listFile = []
                for i in range (0,numOfFile):
                    listFile.append(receive_message())
                print(*listFile,sep = "\n")           
            else:
                os.system('cls')
                print(f"Welcome {userName}^^")
main()