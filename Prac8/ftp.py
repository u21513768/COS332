import socket
import time
import os
import hashlib

def ftp_get(host, port, username, password, remote_file, local_file):
    # Connect to the FTP server
    ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_socket.connect((host, port))
    response = ftp_socket.recv(4096).decode()
    print(response)
    
    # Send username
    ftp_socket.send(f"USER {username}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    print(response)
    
    # Send password
    ftp_socket.send(f"PASS {password}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    print(response)
    
    # Send PASV command
    ftp_socket.send(b"PASV\r\n")
    response = ftp_socket.recv(4096).decode()
    print(response)
    
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
    print(response)
    
    # Get file data
    file_data = b""
    while True:
        chunk = data_socket.recv(4096)
        if not chunk:
            break
        file_data += chunk
    
    # Save file locally
    with open(local_file, "wb") as f:
        f.write(file_data)
    
    # Close connections
    data_socket.close()
    ftp_socket.close()

def calculate_file_hash(file_path):
    if os.path.exists(file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            buf = f.read(4096)
            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(4096)
        return hasher.hexdigest()
    else:
        print(f"File '{file_path}' does not exist.")
        return None

def get_file_modification_time(host, port, username, password, remote_file):
    # Connect to the FTP server
    ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ftp_socket.connect((host, port))
    response = ftp_socket.recv(4096).decode()
    # print(response)
    
    # Send username
    ftp_socket.send(f"USER {username}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    # print(response)
    
    # Send password
    ftp_socket.send(f"PASS {password}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    # print(response)
    
    # Send MDTM command to get modification timestamp
    ftp_socket.send(f"MDTM {remote_file}\r\n".encode())
    response = ftp_socket.recv(4096).decode()
    # print(response)
    
    # Extract modification timestamp from the response
    parts = response.split(" ")[1].strip()
    timestamp = time.strptime(parts, "%Y%m%d%H%M%S")
    
    # Close connection
    ftp_socket.close()
    
    return time.mktime(timestamp)  # Convert to epoch time

def monitor_file(local_file, remote_file):
    # Get initial file hash
    remote_hash = calculate_file_hash(remote_file)
    server_mtime = get_file_modification_time(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
    print("Initial server file modification time:", time.ctime(server_mtime))
    
    # Monitor the file for changes
    while True:
        # Wait for 5 seconds
        time.sleep(5)
        current_time = time.time()
        
        # Calculate current file hash
        current_hash = calculate_file_hash(local_file)
        
        # Compare hashes
        if current_hash != remote_hash:
            print(f"File '{local_file}' has been modified!")
            # Call the FTP function to retrieve the file
            ftp_get(ftp_host, ftp_port, ftp_username, ftp_password, remote_file, local_file)
            print(f"File '{local_file}' has been updated.")

            new_file_hash = calculate_file_hash(local_file)
            if new_file_hash != remote_hash:
                remote_hash = new_file_hash
        
        # Check modification timestamp of the server file
        current_server_mtime = get_file_modification_time(ftp_host, ftp_port, ftp_username, ftp_password, remote_file)
        
        # Compare server file modification time with the last iteration
        if current_server_mtime > server_mtime:
            print(f"Detected change in server file. Time difference: {current_server_mtime - current_time} seconds")
            ftp_get(ftp_host, ftp_port, ftp_username, ftp_password, remote_file, local_file)
            print("Local file has been updated from server.")
            server_mtime = current_server_mtime
            new_file_hash = calculate_file_hash(local_file)
            if new_file_hash != remote_hash:
                remote_hash = new_file_hash

        print("No changes detected.")

# Example usage
ftp_host = "localhost"
ftp_port = 21
ftp_username = "quintin"
ftp_password = "1235"
remote_file = "/srv/ftp/file.txt"
local_file = "/home/quintin/COS332/Prac8/file.txt"

# Start monitoring the file
monitor_file(local_file, remote_file)
