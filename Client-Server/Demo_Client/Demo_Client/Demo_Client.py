﻿import socket
import os
import time 
import sys
header = 64
formatMsg = 'utf-8'

serverPort = 65432
serverIP = '192.168.0.100'

client= socket.socket(socket.AF_INET, socket.SOCK_STREAM)

addr = (serverIP,serverPort)

client.connect(addr)
def handle_duplicate_file_name(fileName, saveDirectory):
    name, extend = os.path.splitext(fileName) #Phân tích tên file thành tên và phần mở rộng.
    listFile = os.listdir(saveDirectory) #Liệt kê ra danh sách các file đã có trong thư mục 
    if (name+extend)  in listFile:
        fileDuplicate = name +' (1)'+ extend
        cnt = 1
        while fileDuplicate in listFile:
           cnt = cnt + 1
           fileDuplicate = name + f' ({cnt})' + extend
        fileName = fileDuplicate
    return fileName
def download_file(fileName, saveDir):
    #Kiểm tra tính hợp lệ của saveDir
    if not os.path.isdir(saveDir):
        print("Folder is not exist or invalid input")
        return
    #Gửi tên file đi 
    send_message(fileName)
    res = receive_message()
    if res == '0':
        print("File does not exist or your file name is wrong")
        return
    #Nhận phản hồi từ phía server.
    handle_duplicate_file_name(fileName,saveDir)
    #Nếu phản hồi là file tồn tại
    filePath = os.path.join(saveDir,fileName) #Tạo đường dẫn đến file 
    #Ghi file
    fout = open(filePath, "wb")
    #Nhận kích thước file sẽ gửi
    sizeOfFile = receive_message()
    sizeOfFile = int(sizeOfFile)
    totalBytes = 0
    #Đặt bộ đếm thời gian
    start = time.time()
    while True:
        # Tin nhắn đầu tiên là độ dài của nội dung mà client có thể nhận
        fileLength = client.recv(header).decode(formatMsg)
        
        if not fileLength:
            break  # Nếu fileLength rỗng, thoát vòng lặp
        fileLength = int(fileLength) #Chuyển kích thước dạng chuỗi về dạng số nguyên
        
        if fileLength == 0: #Đến khi hết dữ liệu thì không ghi nữa, thoát vòng lặp 
            break
        
        data = client.recv(fileLength)
        
        if not data:    
            break  # Nếu không có dữ liệu, thoát vòng lặp
        fout.write(data)  # Ghi dữ liệu vào file
        #Tính tổng số bytes đã nhận
        totalBytes += len(data)
        #Khoảng thời gian
        duration = time.time() - start
        
        #Phần trăm hoàn thành
        process = (totalBytes/sizeOfFile)*100
        if duration > 0:
            sys.stdout.write(f"\rProcess: {process:.2f}%")  # Hiển thị trên một dòng
            sys.stdout.flush()  # Cập nhật ngay lập tức
    if totalBytes == sizeOfFile:
        print("\nClient has received this file.")   
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
def normalize_input(request):
    #Loại bỏ kí tự, khoảng trắng thừa đầu, cuối
    request.strip()
    
    #Tách thành 2 phần (Hoặc 1 phần)
    parts = request.split(maxsplit = 1)
    command = ""
    filePath = ""
    if len(parts) > 2 or len(parts) < 1:
        print("Invalid input")

    if len(parts)==2:
        command = parts[0]
        filePath = parts[1]
        #Chuẩn hóa đường dẫn
        filePath.strip()
        if filePath.startswith('"') and filePath.endswith('"'):
            filePath = filePath[1:-1]
        if not os.path.exists(filePath):
            print("Your path isn't exists")    
    if len(parts) == 1:
        command = parts[0]
    return command, filePath
    
        

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
            command = ""
            filePath = ""
            command, filePath = normalize_input(request)
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
            elif command.strip().lower()=='download':
                print("List available file")
                numOfFile = int(receive_message())
                listFile = []
                for i in range (0,numOfFile):
                    listFile.append(receive_message())
                print(*listFile,sep = "\n")   
                saveDir = input("Input address to save file: ")
                fileName = input("Input file name you want to download: ")
                if saveDir.startswith('"') and saveDir.endswith('"'):
                    saveDir = saveDir[1:-1]
                download_file(fileName,saveDir)
            else:
                print("Please input again")
                os.system('pause')
                os.system('cls')
                print(f"Welcome {userName}^^")
main()