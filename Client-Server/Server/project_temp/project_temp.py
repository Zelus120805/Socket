
#Code cho server
from genericpath import exists
from logging import raiseExceptions
from re import L
import socket
from tabnanny import filename_only
import threading
import os
import datetime
from tkinter import CURRENT
header = 64
formatMsg = 'utf-8'

#Khai báo số hiệu cổng
serverPort = 65432
serverIP = socket.gethostbyname(socket.gethostname())
#Chỉ định giao thức TCP

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#Gắn socket với địa chỉ addr(IP,portNumber)

addr = (serverIP,serverPort) #Định nghĩa một tuple địa chỉ
server.bind(addr) #Kết nối socket với địa chỉ.
def get_current_dirname(fileName):
    baseDir = os.path.dirname(os.path.abspath(__file__))

    # Tạo đường dẫn tới file  trong thư mục Demo_Server
    filePath = os.path.join(baseDir, fileName)
    # Mở file
    return filePath


def receive_message(socketClient, addrClient):
    msgLength = int(socketClient.recv(header).decode(formatMsg))
    msgContent = socketClient.recv(msgLength).decode(formatMsg)
    return msgContent
 
def read_file_user():
    fileUsers = open(get_current_dirname('Users.txt'),"r")
    listUsers = {}
    for line in fileUsers:
        n,p = line.strip().split(",")
        listUsers[n.strip()] = p.strip()
    fileUsers.close()
    return listUsers
listUsers = read_file_user()
print(listUsers)
def client_register(socketClient, addrClient):
    userName = receive_message(socketClient, addrClient)
   
    password = receive_message(socketClient, addrClient)
    
    if userName in listUsers:
        print("Username has been used. Please change your username.")
    else:
        fout = open(get_current_dirname('Users.txt'),"r")
    
def client_login(socketClient, addrClient):
    #Nhận tên đăng nhập 
    userName = receive_message(socketClient, addrClient)
   
    #Nhận mật khẩu
    password = receive_message(socketClient, addrClient)
    
    #Kiếm tra tên đăng nhập
    if userName in listUsers:
        if listUsers[userName] == password:
            socketClient.send(str(1).encode(formatMsg)) #Gửi phản hồi đăng nhập đúng
            return True,userName,password
    else:
        socketClient.send(str(0).encode(formatMsg)) #Gửi phản hồi đăng nhập sai. 
 
        return False, userName, password 
    
    
    #Nhận tên đăng nhập
    #Nhận mật khẩu
    #<decode nếu cần> và tìm trong file
        #Nếu chưa tồn tại hoặc sai mật khẩu => Báo lỗi và return False
        #Nếu đúng, trả về một tuple (True, tên đăng nhập, mật khẩu)
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

#Hàm chuẩn hóa lệnh nhận được từ client (cmd)
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
def function(socketClient, addrClient, userName, isLogined):
    try: 
        while True:
            requestContent = receive_message(socketClient, addrClient)
            command = ""
            filePath = ""
            command, filePath = normalize_input(requestContent)
                
            if command.strip().lower() == 'close':
            
                socketClient.close()
                print(f"Disconnected from {addrClient}")
                return False
            
            if command.strip().lower() == 'logout':
                isLogined = False
                return isLogined
            elif command.strip().lower() == 'upload' and filePath:
                receive_file_from_client(socketClient,addrClient,filePath,userName)
            elif command.strip().lower()=='view':
                send_file_to_client_v2(socketClient,addrClient)
            elif command.strip().lower() == 'download':
                print("Tới đây!!")
    except: 
        socketClient.close()
        print(f"Disconnected from {addrClient}")
        return
            
def handle_client(socketClient, addrClient):
    print(f"[NEW CONNECTION] {addrClient} connected.")
    #Code đăng nhập ------------------------------------------------------------------
    isLogined = False
    userName = ""
    password = ""
    while not isLogined:
        try:
            isLogined , userName, password = client_login(socketClient,addrClient)
        except:
            socketClient.close()
            print(f"Disconnected from {addrClient}")
            return
    #---------------------------------------------------------------------------------
        while isLogined:
            isLogined = function(socketClient, addrClient, userName, isLogined)
            
def receive_file_from_client(socketClient, addrClient, filePath, userName):
    #"C:\Users\pc\Downloads\CTT105-2-IP&subntting_2.0.pdf"

    #Kiểm tra và tạo thư mục nếu chưa có---------------------------------------------------
    saveDir = get_current_dirname(userName)
    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    #--------------------------------------------------------------------------------------

    fileName = os.path.basename(filePath) #Lấy phần tên file bao gồm cả mở rộng
    
    fileName = handle_duplicate_file_name(fileName,saveDir) #Xử lí file trùng
    
    savePath = os.path.join(saveDir, fileName) #Tạo đường dẫn đến thư mục để lưu
    
    fout = open(savePath, "wb") #Tạo một file mới để ghi dữ liệu vào, mở chế độ nhị phân
    while True:
        # Tin nhắn đầu tiên là độ dài của nội dung mà server có thể nhận
        fileLength = socketClient.recv(header).decode(formatMsg)
        
        if not fileLength:
            break  # Nếu fileLength rỗng, thoát vòng lặp
        fileLength = int(fileLength) #Chuyển kích thước dạng chuỗi về dạng số nguyên
        
        if fileLength == 0: #Đến khi hết dữ liệu thì không ghi nữa, thoát vòng lặp 
            break
        
        data = socketClient.recv(fileLength)
        
        if not data:    
            break  # Nếu không có dữ liệu, thoát vòng lặp
        fout.write(data)  # Ghi dữ liệu vào file
        
    print("File received successfully.")
    # Gửi phản hồi về client sau khi hoàn tất
    socketClient.send("Uploaded successfully!".encode(formatMsg))    
    fout.close()
def send_file_to_client(socketClient, addrClient, filePath):
    
    #Lấy kích thước file
    print(filePath)
    sizeOfFile = os.path.getsize(filePath)
    #Gửi kích thước file cho client
    print(sizeOfFile)
    send_message(socketClient, addrClient,str(sizeOfFile))  #GỬI KÍCH THƯỚC FILE 
    
    try:
        fin = open(filePath, "rb")
    except:
        print("Cannot open this file")
        return False
    
    totalBytes = 0
    while totalBytes < sizeOfFile:
        data = fin.read(1024)# Mỗi lần đọc tối đa 1Kb
        if not data:
             break
        
        finLength = len(data)
        sendLength = str(finLength).encode()
        sendLength += b' '*(header - len(sendLength))
        socketClient.send(sendLength)
        socketClient.send(data)
        totalBytes += len(data)
    #Tín hiệu kết thúc file
    sendLength = str(0).encode(formatMsg)
    sendLength += b' ' * (header - len(sendLength))
    socketClient.send(sendLength)
    #Code tìm thấy 
         
    #Nếu duyệt hết thư mục vẫn chưa tìm thấy -> Respond: File not found
    #Nếu tìm thấy => Trả về địa chỉ và out vòng lặp
    #Mở file lên đọc -> Gửi kích thước file -> Gửi kích thước mỗi lần -> gửi nội dung mỗi lần
    #Gửi tín hiệu đã gửi file cho client. 
    # 
    pass
def send_message(socketClient, addrClient, msg):
    msgContent = msg.encode(formatMsg)
    msgLength = len(msgContent)
    sendLength = str(msgLength).encode(formatMsg)
    sendLength += b' '*(header - len(sendLength))
    socketClient.send(sendLength)
    socketClient.send(msgContent)
class Node:
    def __init__(self, fileName, size, dateModified):
        self.name = fileName
        self.size = size
        self.dateModified = dateModified 
        self.children = []
    def add_child(self, newNode):
        self.children.append(newNode)

#-test hàm------------------------------------------------------
class Node:
    def __init__(self, fileName, size, dateModified, path, level):
        self.level = level
        self.name = fileName
        self.size = size
        self.dateModified = dateModified 
        self.path = path
        self.children = []
    def add_child(self, newNode):
        self.children.append(newNode)

def get_info(filePath):
    #Lấy kích thước file
    sizeOfFile = os.path.getsize(filePath)
                
    #Lấy thời gian (time modified)
    timeStamp = os.path.getmtime(filePath)
    dateModified = datetime.datetime.fromtimestamp(timeStamp).date()
    return sizeOfFile, dateModified
def traversal_folder(folderPath, root, level):
    listItem = os.listdir(folderPath)
    for item in listItem:
        itemPath = os.path.join(folderPath,item)
        size, date = get_info(itemPath)
        newNode = Node(item, size, date, itemPath, level)
        root.add_child(newNode)
        if os.path.isdir(itemPath):
            traversal_folder(itemPath, newNode, level + 1)
def send_file_to_client_v2(socketClient, addrClient):
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    currentDir = os.getcwd()
    print(currentDir)
    items = os.listdir(currentDir)
    #Khởi tạo cây thư mục. 
    root = Node('availableFile',0,'','',0)
    for name in items:
        itemPath = os.path.join(currentDir, name)
        if os.path.isdir(itemPath):
            size, date = get_info(itemPath)
            newNode = Node(name, size, date, itemPath, 1)
            root.add_child(newNode)
            traversal_folder(itemPath,newNode,2)
    preOrder(root)
    send_preOrder(socketClient,addrClient, root)
def send_preOrder(socketClient, addrClient, root):
    if not root:
        return
    send_message(socketClient,addrClient,str(len(root.children))) #Gửi số con của node đó, báo hiệu rằng n node tiếp theo phải nhận là con của nó. 
    send_message(socketClient,addrClient,root.name) #Gửi tên
    send_message(socketClient,addrClient,str(root.size)) #Gửi kích thước
    send_message(socketClient,addrClient,str(root.dateModified)) #Gửi ngày sửa đổi
    send_message(socketClient,addrClient,str(root.path)) #Gửi ngày sửa đổi
    for child in root.children:
        send_preOrder(socketClient, addrClient, child)
def preOrder(root):
    if not root:
        return

    # Thụt đầu dòng theo cấp độ
    indent = "  " * root.level
    if os.path.isdir(root.path):
        print(f"{indent}- {root.name} (Size: {root.size}, Modified: {root.dateModified}) - Level {root.level}")
    else:
        print(f"{indent}- {root.name} (Size: {root.size}, Modified: {root.dateModified}) - Level {root.level}")
    # Duyệt qua các nút con
    for child in root.children :
        preOrder(child)
            
                

def send_list_file_to_client(socketClient, addrClient):
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    currentDir = os.getcwd()
    print(currentDir)
    items = os.listdir(currentDir)
    listFile = []
    
    for name in items:
        if os.path.isdir(name): #Nếu đó là thư mục, truy cập vào thư mục đó
            
            #Liệt kê tất cả file, thư mục (Gọi chung là items) vào list "fileInName
            fileInName = os.listdir(name)
            
            #Duyệt thư mục name
            for fileName in fileInName:
                
                #Tạo đường dẫn đến file
                filePath = os.path.join(os.path.join(currentDir,name),fileName)
                
                #Lấy kích thước file
                sizeOfFile = os.path.getsize(filePath)
                
                #Lấy thời gian (time modified)
                timeStamp = os.path.getmtime(filePath)
                dateModified = datetime.datetime.fromtimestamp(timeStamp).date()
                
                #Thêm vào danh sách listFile
                listFile.append((fileName, sizeOfFile, dateModified))
                
    send_message(socketClient,addrClient,str(len(listFile)))
    for file in listFile:
        send_message(socketClient,addrClient,file[0]) #Gửi tên
        send_message(socketClient,addrClient,str(file[1])) #Gửi kích thước
        send_message(socketClient,addrClient,str(file[2])) #Gửi ngày sửa đổi
def start_server():
    #Lắng nghe chờ đợi kết nối
    server.listen()
    print(f"Server is listening on {addr}")
    
    #Khi client tới
    while True:
        #Lấy địa chỉ client và tạo một socket riêng, dành cho việc trao đổi với client này
        newClient, newAddr = server.accept()
        
        #Tạo luồng xử lí cho client này
        newThread = threading.Thread(target = handle_client, args = (newClient,newAddr),daemon = True)
        
        #Bắt đầu luồng xử lí này.
        newThread.start()

        print(f"[ACTIVE CONNECTION] {threading.activeCount() - 1}")
        
        
start_server()
print(serverIP)

