import socket
import tkinter as tk
import os
import module1
import sys
import time
from tkinter import filedialog  # Import thư viện mở File Explorer

header =  64
FORMAT = 'utf-8'
IP = '192.168.0.100'
PORT = 65432
ADDR = (IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

localIP, localPORT = client.getsockname()

root = tk.Tk()
#Định nghĩa toàn cục entry
entry = None
#Hàm upload_file------------------------------------------------------------------------------------------\
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
    sendLength = str(0).encode(FORMAT)
    sendLength += b' ' * (header - len(sendLength))
    client.send(sendLength)
    
    response = client.recv(2048).decode(FORMAT)
    print(f"\n[SERVER RESPONSE]:{response}")
    fin.close()
    if totalBytes == sizeOfFile:
        return True
    else:
        return False
#----------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------
def choose_file():
    global entry
    file_path = filedialog.askopenfilename(title="Select File to Upload")  # Mở File Explorer để chọn file
    if file_path:  # Nếu người dùng chọn file
        print(f"File selected: {file_path}")  # In ra đường dẫn file
        #send_message(f'upload {file_path}')
        entry.delete(0, tk.END)  # Xóa nội dung cũ trong ô nhập
        entry.insert(0, f'upload {file_path}')  # Thêm chuỗi upload {file_path} vào ô nhập tin nhắn
        #upload_file(file_path)  # Gọi hàm upload_file với đường dẫn file

#-------------------------------------------------------------------

def send_message(msg):
    msgContent = msg.encode(FORMAT)
    msgLength = len(msgContent) 
    sendLength = str(msgLength).encode(FORMAT)
    sendLength += b' '*(header - len(sendLength))
    client.send(sendLength)
    client.send(msgContent)

def client_login(username, password):
    if username and password:
        send_message(username)
        send_message(password)
        res = client.recv(1).decode(FORMAT)
        if res=='1':
            return True, username
        else:
            return False, None
    else:
        return False, None


def menu_GUI(username):
    global entry #Truyền tham chiếu biến toàn cục entry vào hàm 
    root.title("GUI")
    for widget in root.winfo_children():
        widget.destroy()
    
    def normalize_input(request):
        #Loại bỏ kí tự, khoảng trắng thừa đầu, cuối
        request = request.strip()
        
        #Tách thành 2 phần (Hoặc 1 phần)
        parts = request.split(maxsplit = 1)
        command = ""
        filePath = ""
        warn=""

        if len(parts) < 2:
            command=parts[0] # Hello
        else:
            command = parts[0]
            filePath = parts[1]

            if filePath.startswith('"') and filePath.endswith('"'):
                filePath = filePath[1:-1]
            
            if command=="upload" or command=="download":
                if not os.path.exists(filePath):
                    warn="Your path isn't exists"

        return command, filePath, warn

    def ib_message(event=None):
        message = entry.get()
        if message.isspace():
            entry.delete(0, tk.END)
        elif (message=="logout" or message=="LOGOUT"):
            send_message(message)
            root.after(2000, lambda: menu_login())
          
        elif message:

            # Tạo label chứa tin nhắn và thêm vào vùng cuộn
            message_frame = tk.Frame(scrollable_frame)
            message_frame.pack(anchor="e", fill="x")
            
            # Tạo Label cho tin nhắn, căn phải
            label = tk.Label(message_frame, text=message, font=("Arial", 15), bg="white", anchor="e", width=56)
            label.pack(fill="x")
            
            # Tự động cuộn xuống cuối
            root.after(20, lambda: canvas.yview_moveto(1.0))
            
            # Xóa nội dung trong entry sau khi gửi tin nhắn
            entry.delete(0, tk.END)

            command, filePath, warn = normalize_input(message)
            if (warn != ""):
                warn_label=tk.Label(message_frame, text=warn, font=("Arial", 15), bg="lightyellow", fg="crimson", anchor="e", width=70)
                warn_label.pack(fill="x")
                
            #Đoạn này khá giống với cmd. Nếu command là upload và filePath tồn tại, thì gửi tin nhắn đó cho message và thực hiện upload_file
            if command.strip().lower()=='upload' and os.path.exists(filePath):
                send_message(message)
                isUploaded = upload_file(filePath)
            #Nếu isUploaded = True nghĩa là upload thành công, thì in ra phản hồi của Server lên message_frame. 
            if isUploaded:
                label = tk.Label(message_frame, text='File has been uploaded', font=("Tahoma", 15), bg="red", anchor="w", width=56)
                label.pack(fill="x")
            else:
                label = tk.Label(message_frame, text='Fail to upload this file', font=("Tahoma", 15), bg="red", anchor="w", width=56)
                label.pack(fill="x")
                
    server_label = tk.Label(root, text=f"{username} [{localIP}, {localPORT}]", font=("Arial", 15, "bold"),  bg="green", fg="yellow")
    server_label.pack(padx=30, pady=10, side="top", anchor="w")
    main_frame = tk.Frame(root, borderwidth=2, relief="solid")
    main_frame.pack(padx=20, pady=(5, 10), fill="both", expand=True)

    # Tạo canvas và scrollbar cho vùng tin nhắn
    canvas = tk.Canvas(main_frame, bg="white")
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    # Liên kết canvas với scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="center")

    # Cập nhật vùng cuộn khi nội dung thay đổi
    scrollable_frame.bind("<Configure>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    # Liên kết sự kiện cuộn chuột với canvas
    canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(-1 * (event.delta // 120), "units"))  # Cuộn trên Windows

    # Vùng nhập tin nhắn và gửi
    entry_frame = tk.Frame(root)
    entry_frame.pack(side="bottom", anchor="s", fill="x", pady=5)  # Neo khung nhập vào cuối cửa sổ và cho phép giãn

    # Nút thứ nhất (Góc trái)
    button1 = tk.Button(entry_frame, text="Upload", font=("Arial", 13), command = choose_file)
    button1.pack(side="left", padx=(10, 5))  # Cách lề trái 10px, cách nút thứ hai 5px

    # Nút thứ hai (Kế bên nút 1)
    button2 = tk.Button(entry_frame, text="Download", font=("Arial", 13))
    button2.pack(side="left", padx=(0, 10))  # Cách nút 1 không gian 0px, cách khung nhập 10px

    # Ô nhập tin nhắn
    entry = tk.Entry(entry_frame, font=("Arial", 15))
    entry.pack(side="left", fill="x", expand=True, padx=(0, 7))  # Giãn khung nhập dữ liệu theo chiều ngang

    # Nút "Send"
    send_button = tk.Button(entry_frame, text="Send", font=("Arial", 13), command=ib_message)
    send_button.pack(side="left", padx=(0, 15))  # Giữ cố định ở góc phải



def menu_login():
    for widget in root.winfo_children():
        widget.destroy()

    root.title("Login")
    root.geometry("700x500")  # Tăng kích thước cửa sổ chính
    #root.attributes("-topmost", True)

    # Tạo một khung lớn hơn
    main_frame = tk.Frame(root, bg="lightblue", borderwidth=2, relief="flat")
    main_frame.pack(padx=50, pady=50, fill="both", expand=True)

    # Thêm tiêu đề
    label = tk.Label(main_frame, text="Login", font=("Arial", 30, "bold"), bg="lightblue")
    label.pack(side="top", anchor="center", pady=10)

    # Ô nhập tên đăng nhập
    user_frame = tk.Frame(main_frame, bg="lightblue")
    user_frame.pack(side="top", anchor="center", pady=10)
    user_label = tk.Label(user_frame, text="Username:", bg="lightblue", font=("Arial", 15))
    user_label.pack(side="left")
    user_entry = tk.Entry(user_frame, font=("Arial", 12), width=25)
    user_entry.pack(side="left", padx=5)

    # Ô nhập mật khẩu
    pass_frame = tk.Frame(main_frame, bg="lightblue")
    pass_frame.pack(side="top", anchor="center", pady=10)
    pass_label = tk.Label(pass_frame, text="Password:", bg="lightblue", font=("Arial", 15))
    pass_label.pack(side="left")
    pass_entry = tk.Entry(pass_frame, show="*", font=("Arial", 12), width=25)
    pass_entry.pack(side="left", padx=5)

    #user_entry.focus()

    def click_reset():
        print(" ")

    # Ô đặt lại mật khẩu
    reset_button = tk.Button(main_frame, text="Reset password", font=("Arial", 12, "bold"), bg="lightblue", fg = "purple", command=click_reset)
    reset_button.pack(pady=15)

    def click_Login():
        username = user_entry.get()
        password = pass_entry.get()

        isLogined, username = client_login(username, password)
        if isLogined:
            success_label = tk.Label(main_frame, text=f"Login successful! Welcome, {username}", font=("Arial", 17, "bold"), bg="yellow", fg = "red")
            success_label.pack(pady=15)
            root.after(2000, lambda: menu_GUI(username))
        else:
            fail_label = tk.Label(main_frame, text="Login failed! Invalid username or password.", font=("Arial", 17, "bold"), bg="yellow", fg = "red")
            fail_label.pack(pady=15)
            root.after(2000, lambda: fail_label.destroy())

    # Nút đăng nhập
    login_button = tk.Button(main_frame, text="Login", bg="lightgreen", font=("Arial", 15, "bold"), command=click_Login)
    login_button.pack(pady=15)

menu_login()
root.mainloop()