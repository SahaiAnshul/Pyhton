import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
import socket
from datetime import datetime

# Constants
SERVER_HOST = '127.0.0.1'  # Localhost IP
SERVER_PORT = 12345  # Replace with your server port

# Global variables for login credentials
registered_devices = {
    "user": "user",  # Example device already registered
}

# Global variables for upload and download counts
successful_uploads = 0
failed_uploads = 0
successful_downloads = 0
failed_downloads = 0

# Lists to store file information for category
uploaded_files = []
downloaded_files = []

# Function to handle file uploads
def upload_file():
    global successful_uploads, failed_uploads
    file_path = filedialog.askopenfilename()
    if file_path:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_HOST, SERVER_PORT))

                # Send file name
                file_name = os.path.basename(file_path)
                s.sendall(file_name.encode())

                # Send file content
                with open(file_path, 'rb') as f:
                    file_size = os.path.getsize(file_path)
                    sent_bytes = 0
                    while True:
                        data = f.read(1024)
                        if not data:
                            break
                        s.sendall(data)
                        sent_bytes += len(data)

            messagebox.showinfo("Upload Complete", f"File '{file_name}' uploaded successfully!")
            successful_uploads += 1
            uploaded_files.append((file_name, file_size, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            update_manage_uploads_button()
            update_category_table()

        except Exception as e:
            messagebox.showerror("Upload Failed", f"Failed to upload file: {e}")
            failed_uploads += 1
            update_manage_uploads_button()

# Function to handle file downloads
def download_file():
    global successful_downloads, failed_downloads
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_HOST, SERVER_PORT))

            # Request file list (not implemented in this basic example)

            # Receive file name
            file_name = s.recv(1024).decode()

            # Receive file content
            save_path = filedialog.asksaveasfilename(initialfile=file_name, defaultextension=".*")
            if save_path:
                with open(save_path, 'wb') as f:
                    while True:
                        data = s.recv(1024)
                        if not data:
                            break
                        f.write(data)

                file_size = os.path.getsize(save_path)
                messagebox.showinfo("Download Complete", f"File '{file_name}' downloaded successfully!")
                successful_downloads += 1
                downloaded_files.append((file_name, file_size, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                update_manage_downloads_button()
                update_category_table()

    except Exception as e:
        messagebox.showerror("Download Failed", f"Failed to download file: {e}")
        failed_downloads += 1
        update_manage_downloads_button()

# Function to update "Manage Uploads" button label
def update_manage_uploads_button():
    btn_upload_manager.config(text=f"Manage Uploads\nSuccessful: {successful_uploads}\nFailed: {failed_uploads}")

# Function to update "Manage Downloads" button label
def update_manage_downloads_button():
    btn_download_manager.config(text=f"Manage Downloads\nSuccessful: {successful_downloads}\nFailed: {failed_downloads}")

# Function to open the manager window
def open_manager():
    manager_window = tk.Toplevel(root_main)
    manager_window.title("Manager")
    manager_window.geometry("500x300")

    # Create a canvas for scrollable content
    canvas = tk.Canvas(manager_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(manager_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame for manager buttons
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    # Buttons for managing uploads, downloads, viewing history
    global btn_upload_manager, btn_download_manager
    btn_upload_manager = tk.Button(frame, text=f"Manage Uploads\nSuccessful: {successful_uploads}\nFailed: {failed_uploads}", command=manage_uploads, bg="#2ECC71", fg="white", padx=10)
    btn_upload_manager.pack(pady=10, padx=10, fill=tk.X)

    btn_download_manager = tk.Button(frame, text=f"Manage Downloads\nSuccessful: {successful_downloads}\nFailed: {failed_downloads}", command=manage_downloads, bg="#3498DB", fg="white", padx=10)
    btn_download_manager.pack(pady=10, padx=10, fill=tk.X)

    btn_category = tk.Button(frame, text="Category", command=show_category, bg="#9B59B6", fg="white", padx=10)
    btn_category.pack(pady=10, padx=10, fill=tk.X)

    frame.update_idletasks()  # Update the frame

    # Configure canvas scroll region
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Function to open manage uploads window
def manage_uploads():
    message = f"Total Uploads:\nSuccessful: {successful_uploads}\nFailed: {failed_uploads}"
    messagebox.showinfo("Manage Uploads", message)

# Function to open manage downloads window
def manage_downloads():
    message = f"Total Downloads:\nSuccessful: {successful_downloads}\nFailed: {failed_downloads}"
    messagebox.showinfo("Manage Downloads", message)

# Function to show category window
def show_category():
    global category_window, tree, canvas

    category_window = tk.Toplevel(root_main)
    category_window.title("Category")
    category_window.geometry("500x300")

    # Create a canvas for scrollable content
    canvas = tk.Canvas(category_window)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Add a scrollbar to the canvas
    scrollbar = ttk.Scrollbar(category_window, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Frame for Treeview
    frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor=tk.NW)

    # Create Treeview
    global tree
    tree = ttk.Treeview(frame, columns=("File Name", "Size", "Time"), show='headings')
    tree.heading("File Name", text="File Name")
    tree.heading("Size", text="Size (bytes)")
    tree.heading("Time", text="Time")

    update_category_table()

    tree.pack(fill=tk.BOTH, expand=True)

    frame.update_idletasks()  # Update the frame

    # Configure canvas scroll region
    canvas.config(scrollregion=canvas.bbox(tk.ALL))

# Function to update the category table
def update_category_table():
    if 'tree' in globals():
        # Clear existing rows
        for row in tree.get_children():
            tree.delete(row)

        # Insert uploaded files
        for file in uploaded_files:
            tree.insert("", tk.END, values=(file[0], file[1], file[2]))

        # Insert downloaded files
        for file in downloaded_files:
            tree.insert("", tk.END, values=(file[0], file[1], file[2]))

# Function to handle the login process with animation
def login():
    entered_username = entry_username.get()
    entered_password = entry_password.get()

    # Check if username and password match the registered devices
    if entered_username in registered_devices and registered_devices[entered_username] == entered_password:
        # Animation effect: Change background color gradually
        animate_login_success(root_login)
        
        messagebox.showinfo("Login Successful", f"Welcome, {entered_username}!")

        # Destroy login window and open main application window
        root_login.withdraw()  # Hide the login window
        open_main_application()

    else:
        # Animation effect: Shake login window
        animate_login_failure(root_login)
        
        messagebox.showerror("Login Failed", "Invalid username or password")

# Function to animate successful login (change background color)
def animate_login_success(window):
    original_color = window.cget("bg")
    for _ in range(5):
        window.configure(bg="green")
        window.update()
        window.after(100)
        window.configure(bg=original_color)
        window.update()

# Function to animate failed login (shake window)
def animate_login_failure(window):
    original_x = window.winfo_x()
    original_y = window.winfo_y()
    for _ in range(5):
        window.geometry(f"300x200+{original_x + 10}+{original_y}")
        window.update()
        window.after(50)
        window.geometry(f"300x200+{original_x - 10}+{original_y}")
        window.update()
        window.after(50)
    window.geometry(f"300x200+{original_x}+{original_y}")

# Function to register a new device
def register():
    new_username = entry_username.get()
    new_password = entry_password.get()

    if new_username and new_password:
        if new_username not in registered_devices:
            registered_devices[new_username] = new_password
            messagebox.showinfo("Registration Successful", "Device registered successfully!")
        else:
            messagebox.showerror("Registration Failed", "Username already exists.")
    else:
        messagebox.showerror("Registration Failed", "Username and password cannot be empty.")

# Function to open the main application window after successful login
def open_main_application():
    global root_main

    # Create the main application window
    root_main = tk.Tk()
    root_main.title("File Sharing App")
    root_main.geometry("300x250")
    root_main.configure(bg="#34495E")  # Set background color

    # Buttons for file upload, download, and manager
    btn_upload = tk.Button(root_main, text="Upload File", command=upload_file, bg="#3498DB", fg="white", padx=10)
    btn_upload.pack(pady=10, padx=10, fill=tk.X)

    btn_download = tk.Button(root_main, text="Download File", command=download_file, bg="#E74C3C", fg="white", padx=10)
    btn_download.pack(pady=10, padx=10, fill=tk.X)

    btn_manager = tk.Button(root_main, text="Manager", command=open_manager, bg="#2C3E50", fg="white", padx=10)
    btn_manager.pack(pady=10, padx=10, fill=tk.X)

    # Label to display username
    label_username = tk.Label(root_main, text=f"Logged in as: {entry_username.get()}", bg="#34495E", fg="white")
    label_username.pack(pady=10)

    # Button to logout
    btn_logout = tk.Button(root_main, text="Logout", command=logout, bg="#F39C12", fg="white", padx=10)
    btn_logout.pack(pady=10, padx=10, fill=tk.X)

    root_main.mainloop()

# Function to handle the logout process
def logout():
    root_main.destroy()  # Destroy the main application window
    root_login.deiconify()  # Show the login window again

# Function to create and show the login window
def show_login():
    global root_login, entry_username, entry_password

    # Create the login window
    root_login = tk.Tk()
    root_login.title("Login")
    root_login.geometry("300x200")
    root_login.configure(bg="#3498DB")  # Set background color

    # Username label and entry
    label_username = tk.Label(root_login, text="Username:", bg="#3498DB", fg="white")
    label_username.pack(pady=5)
    entry_username = tk.Entry(root_login)
    entry_username.pack(pady=5)

    # Password label and entry
    label_password = tk.Label(root_login, text="Password:", bg="#3498DB", fg="white")
    label_password.pack(pady=5)
    entry_password = tk.Entry(root_login, show="*")
    entry_password.pack(pady=5)

    # Login button
    btn_login = tk.Button(root_login, text="Login", command=login, bg="#2E86C1", fg="white")
    btn_login.pack(pady=10, padx=10, fill=tk.X)

    # Register button
    btn_register = tk.Button(root_login, text="Register", command=register, bg="#2E86C1", fg="white")
    btn_register.pack(pady=10, padx=10, fill=tk.X)

    root_login.mainloop()

# Entry point of the application
if __name__ == "__main__":
    show_login()
