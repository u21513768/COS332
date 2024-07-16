import socket
import time
import hashlib
import os

def ftp_get_file_data(host, port, username, password, remote_file):
    # Connect to the FTP server
    ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_socket.connect((host, port))
    response = ftp_socket.recv(4096).decode()
    
    # Send username
    ftp_socket.send(f"USER {username}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    
    # Send password
    ftp_socket.send(f"PASS {password}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    
    # Send PASV command
    ftp_socket.send(b"PASV\r\n")
    response = ftp_socket.recv(4096).decode()
    
    # Extract data port from the response
    parts = response.split('(')[-1].split(')')[0].split(',')
    ip_address = '.'.join(parts[:-2])
    data_port = int(parts[-2]) * 256 + int(parts[-1])
    
    # Connect to data port
    data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_socket.connect((ip_address, data_port))
    
    # Send RETR command
    ftp_socket.send(f"RETR {remote_file}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    
    # Get file data
    file_data = b""
    while True:
        chunk = data_socket.recv(4096)
        if not chunk:
            break
        file_data += chunk
    
    # Close connections
    data_socket.close()
    ftp_socket.close()
    
    return file_data

def calculate_hash(data):
    hasher = hashlib.md5()
    hasher.update(data)
    return hasher.hexdigest()

def get_file_modification_time(host, port, username, password, remote_file):
    # Connect to the FTP server
    ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_socket.connect((host, port))
    response = ftp_socket.recv(4096).decode()
    
    # Send username
    ftp_socket.send(f"USER {username}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    
    # Send password
    ftp_socket.send(f"PASS {password}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    
    ftp_socket.send(f"MDTM {remote_file}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    
    parts = response.split(" ")[1].strip()
    timestamp = time.strptime(parts, "%Y%m%d%H%M%S")
    
    # Close connection
    ftp_socket.close()
    
    return time.mktime(timestamp)  # Convert to epoch time

def monitor_file(local_file, remote_file):
    # Get initial remote file data and its hash
    remote_file_data = ftp_get_file_data(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
    remote_hash = calculate_hash(remote_file_data)
    server_mtime = get_file_modification_time(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
    print("Initial server file modification time:", time.ctime(server_mtime))
    
    # Ensure the local file exists, if not, download it
    if not os.path.exists(local_file):
        with open(local_file, "wb") as f:
            f.write(remote_file_data)
        print(f"Local file '{local_file}' did not exist and has been downloaded from the server.")
    
    # Monitor the file for changes
    while True:
        # Wait for 5 seconds
        time.sleep(5)
        current_time = time.time()
        
        # Check if local file exists, if not, download it
        if not os.path.exists(local_file):
            print(f"Local file '{local_file}' has been deleted! Downloading from server.")
            with open(local_file, "wb") as f:
                f.write(remote_file_data)
            print(f"Local file '{local_file}' has been restored from the server.")
        
        # Calculate current local file hash
        with open(local_file, 'rb') as f:
            local_file_data = f.read()
        current_hash = calculate_hash(local_file_data)
        
        # Compare hashes
        if current_hash != remote_hash:
            print(f"File '{local_file}' has been modified!")
            # Retrieve the updated file from the server
            remote_file_data = ftp_get_file_data(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
            with open(local_file, "wb") as f:
                f.write(remote_file_data)
            print(f"File '{local_file}' has been updated.")
            remote_hash = calculate_hash(remote_file_data)
        
        # Check modification timestamp of the server file
        current_server_mtime = get_file_modification_time(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
        
        # Compare server file modification time with the last iteration
        if current_server_mtime > server_mtime:
            print(f"Detected change in server file. Time difference: {current_time - current_server_mtime} seconds")
            remote_file_data = ftp_get_file_data(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
            with open(local_file, "wb") as f:
                f.write(remote_file_data)
            print("Local file has been updated from server.")
            server_mtime = current_server_mtime
            remote_hash = calculate_hash(remote_file_data)
        
        print("No changes detected.")


ftp_host = "localhost"
ftp_port = 21
ftp_username = "quintin"
ftp_password = "1235"
remote_file = "/srv/ftp/file.txt"
local_file = "/home/quintin/COS332/Prac8/file.txt"

# Start 
monitor_file(local_file, remote_file)
