import socket
import tkinter as tk
import os
import json
import sys
import time
from tkinter import filedialog  # Import thư viện mở File Explorer
from tkinter import ttk

header =  64
FORMAT = 'utf-8'
IP = socket.gethostbyname(socket.gethostname())
PORT = 65432
ADDR = (IP, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

localIP, localPORT = client.getsockname()

root = tk.Tk()
#Định nghĩa toàn cục node root
class Node:
    def __init__(self, fileName, size, dateModified):
        self.name = fileName
        self.size = size
        self.dateModified = dateModified
        self.children = []
    def add_child(self, newNode):
        self.children.append(newNode)
nodeRoot = Node(None, None, None)
#Định nghĩa toàn cục entry
entry = None
#-DOWNLOAD FILE - CÁC HÀM PHỤ TRỢ----------------------------------------------------------------------------
def show_list_file_v2():
    global entry
    send_message('view')
    def insert_node(tree, parent_id, node):
        # Loại nút: Folder nếu có children, File nếu không
        node_type = "Folder" if node.children else "File"

        # Thêm nút vào TreeView với các giá trị đúng cột
        node_id = tree.insert(
            parent_id, 
            "end", 
            text=node.name,  # Hiển thị tên ở cột đầu tiên
            values=(node.size, node.dateModified)  # Hiển thị thông tin vào cột còn lại
        )
        # Liên kết node với ID của TreeView
        node_map[node_id] = node

        # Đệ quy thêm các nút con (mặc định thụt lề)
        for child in node.children:
            insert_node(tree, node_id, child)

    def on_double_click(event):
        # Xử lý sự kiện double-click để nạp nút con
        selected_item = tree.selection()[0]  # Lấy ID của nút được chọn
        selected_node = node_map.get(selected_item)  # Tìm node tương ứng

        if selected_node and tree.get_children(selected_item) == ():  # Nếu chưa nạp con
            for child in selected_node.children:
                insert_node(tree, selected_item, child)
    #Xử lí sự kiện nhấn nút
    def on_button_click():
        # Lấy ID của nút được chọn
        selected_item = tree.selection()
        if not selected_item:
            print("No item selected")
            return
        selected_item = selected_item[0]

        # Lấy node tương ứng
        selected_node = node_map.get(selected_item)

        # Kiểm tra loại node
        if selected_node:
            if not selected_node.children:
               entry.delete(0, tk.END)  # Xóa nội dung cũ trong ô nhập
               entry.insert(0, f'{selected_node.name}')  # Thêm chuỗi upload {file_path} vào ô nhập tin nhắn
               list_window.destroy()
    # Nhận dữ liệu
    root_node = Node(None, None, None)
    receive_preorder(root_node)

    # Tạo cửa sổ hiển thị
    list_window = tk.Toplevel()
    list_window.title("TreeView Example")
    list_window.geometry("600x400")

    # Khung chứa TreeView và thanh cuộn
    frame = tk.Frame(list_window)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Định nghĩa các cột
    columns = ("Size", "Date Modified")
    tree = ttk.Treeview(frame, columns=columns, show="tree headings", height=15)
    tree.pack(side="left", fill="both", expand=True)

    # Đặt tiêu đề các cột
    tree.heading("#0", text="Name", anchor="w")  # Cột gốc (hiển thị tên)
    tree.heading("Size", text="Size", anchor="center")
    tree.heading("Date Modified", text="Date Modified", anchor="center")

    # Đặt độ rộng cột
    tree.column("#0", width=250, anchor="w")  # Cột tên
    tree.column("Size", width=100, anchor="center")  # Cột kích thước
    tree.column("Date Modified", width=150, anchor="center")  # Cột ngày sửa đổi

    # Thêm thanh cuộn dọc
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Thêm nút thực hiện hành động
    button_frame = tk.Frame(list_window)
    button_frame.pack(fill="x", padx=10, pady=(0, 10))

    action_button = tk.Button(button_frame, text="Select", font = ('Arial',13), command=on_button_click)
    action_button.pack(side="right")

    # Bản đồ lưu trữ tham chiếu giữa TreeView và Node
    node_map = {}

    # Thêm root node và các con của nó
    insert_node(tree, "", root_node)

    # Gắn sự kiện Double Click
    tree.bind("<Double-1>", on_double_click)
 
#Định nghĩa cây thư mục


#Hàm nhận theo preorder
def receive_preorder(root):
    try:
        #Nhận số con của root. 
        numChild = int(receive_message())
    
        #Nhận tham số tệp tin
        name = receive_message()
        size = receive_message()
        date = receive_message()
    
        if root.name == None:
            root.name, root.size, root.dateModified = (name, size, date)  # Tạo root khi nhận node hợp lệ đầu tiên
            for i in range(numChild):
                receive_preorder(root)
        
        else:
            newNode = Node(name, size, date)
            root.add_child(newNode)

            for i in range(numChild):
                receive_preorder(newNode)
    except Exception as error:
        print(f"{error}")
def preOrder(root,level):
    if not root:
        return

    # Thụt đầu dòng theo cấp độ
    indent = "  " * level
    print(f"{indent}- {root.name} (Size: {root.size}, Modified: {root.dateModified}) - Level {level}")

    # Duyệt qua các nút con
    for child in root.children :
        preOrder(child,level + 1)

#------------------------------------------------------------------------------------------------------------

#HÀM UPLOAD FILE---------------------------------------------------------------------------------------------\
isUploaded = False #Biến global theo dõi quá trình upload
def upload_file(filePath):
    global isUploaded
    upload_window = tk.Toplevel(root)  # Tạo hộp thoại mới
    upload_window.title("Uploading...")
    upload_window.geometry("400x150")
    
    # Thanh tiến trình
    progress_label = tk.Label(upload_window, text="Uploading...", font=("Arial", 14))
    progress_label.pack(pady=10)

    progress_bar = ttk.Progressbar(upload_window, orient="horizontal", mode="determinate", length=300)
    progress_bar.pack(pady=20)
    progress_bar["value"] = 0
    # Nhãn hiển thị phần trăm tiến trình
    percent_label = tk.Label(upload_window, text="0%", font=("Arial", 12))
    percent_label.pack(pady=5)
    
    upload_window.update_idletasks()  # Cập nhật giao diện

    try:
        fin = open(filePath, "rb")
    except:
        print("Cannot open this file")
        return False
    
    sizeOfFile = os.path.getsize(filePath)  # Lấy kích thước file
    totalBytes = 0  # Tính toán tổng số bytes đã tải
    startTime = time.time()  # Thời điểm bắt đầu
    def finish_progress():
        global isUploaded
        # Gửi tín hiệu kết thúc file
        sendLength = str(0).encode(FORMAT)
        sendLength += b' ' * (header - len(sendLength))
        client.send(sendLength)
        
        response = client.recv(2048).decode(FORMAT)
        print(f"\n[SERVER RESPONSE]: {response}")
        
        # Đóng file
        fin.close()
        
        # Cập nhật thanh progress bar
        if totalBytes == sizeOfFile:
            progress_label.config(text='Upload completed!')
            progress_bar["value"] = 100
            upload_window.after(2000, upload_window.destroy)
            isUploaded = True
            return True
        else:
            progress_label.config(text='Upload failed!')
            upload_window.after(2000, upload_window.destroy)
            isUploaded = False
            return False
        
    
    def upload_progress():
                  # Dùng nonlocal để truy cập biến từ ngoài hàm
        nonlocal totalBytes, sizeOfFile
        if totalBytes >= sizeOfFile:
            return finish_progress()  # Kết thúc upload nếu tải xong

        try:
            data = fin.read(1024)  # Đọc tối đa 1KB mỗi lần
            if not data:
                return finish_progress()  # Nếu không còn dữ liệu, kết thúc
            
            finLength = len(data)
            sendLength = str(finLength).encode(FORMAT)
            sendLength += b' ' * (header - len(sendLength))
            client.send(sendLength)
            client.send(data)

            totalBytes += len(data)
       
            duration = time.time() - startTime
            process = (totalBytes / sizeOfFile) * 100
            progress_bar["value"] = process
            percent_label.config(text=f"{process:.2f}%")
            upload_window.update_idletasks()  # Cập nhật giao diện
            upload_window.after(100,upload_progress)  # Gọi lại hàm sau 100ms
            sys.stdout.write(f"\rProcess: {process:.2f}%")  # Hiển thị trên một dòng
            sys.stdout.flush()  # Cập nhật ngay lập tức

        except Exception as e:
            print(f"Error during upload: {e}")
            progress_label.config(text="Upload Failed!")
            upload_window.after(2000, upload_window.destroy)
            return finish_progress()
    upload_progress()
    upload_window.wait_window()  # Chờ cửa sổ tải lên đóng
    return isUploaded
    
#----------------------------------------------------------------------------------------------------------------------------

#CÁC HÀM PHỤ TRỢ-------------------------------------------------------------------------------------------------------------
def choose_file():
    global entry
    file_path = filedialog.askopenfilename(title="Select File to Upload")  # Mở File Explorer để chọn file
    if file_path:  # Nếu người dùng chọn file
        print(f"File selected: {file_path}")  # In ra đường dẫn file
        #send_message(f'upload {file_path}')
        entry.delete(0, tk.END)  # Xóa nội dung cũ trong ô nhập
        entry.insert(0, f'upload {file_path}')  # Thêm chuỗi upload {file_path} vào ô nhập tin nhắn
        #upload_file(file_path)  # Gọi hàm upload_file với đường dẫn file
def receive_message():
    msgContent = '-1'
    msgLength = int(client.recv(header).decode(FORMAT))
    msgContent = client.recv(msgLength).decode(FORMAT)
    return msgContent

def show_list_file():
    send_message('view')  # Yêu cầu server gửi danh sách file
    listFile = []
    numOfFile = int(receive_message())
    for i in range (0,numOfFile):
        fileName = receive_message()
        sizeOfFile = receive_message()
        dateModified = receive_message()
        listFile.append((fileName, sizeOfFile, dateModified))
        
    
    # Tạo cửa sổ danh sách file
    list_window = tk.Toplevel(root)
    list_window.title("Available Files")
    list_window.geometry("500x400")
    #list_window.resizable(False, False)
    
    # Khung chứa Treeview và thanh cuộn
    frame = tk.Frame(list_window)
    frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Tạo Treeview để hiển thị danh sách file
    columns = ("Filename", "Size", "Date Modified")
    tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
    tree.pack(side="left", fill="both", expand=True)

    # Đặt tiêu đề cột
    tree.heading("Filename", text="Filename")
    tree.heading("Size", text="Size (KB)")
    tree.heading("Date Modified", text="Date Modified")

    # Đặt độ rộng cột
    tree.column("Filename", width=250, anchor="w")
    tree.column("Size", width=100, anchor="center")
    tree.column("Date Modified", width=150, anchor="center")

    # Thêm thanh cuộn dọc
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    # Thêm dữ liệu vào Treeview
    for file in listFile:
        size = file[1]
        modified = file[2]
        tree.insert("", "end", values=(file[0], size, modified))

        

#------------------------------------------------------------------------------------------------------------------------------

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
    button2 = tk.Button(entry_frame, text="Download", font=("Arial", 13), command =  show_list_file_v2)
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