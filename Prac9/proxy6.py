import socket
import ssl
import logging
from datetime import datetime
# attempting to implement logging
# updating deleting from thunderbird
# Configure logging
logging.basicConfig(filename='proxy_server.log', level=logging.INFO)

# Add a logger
logger = logging.getLogger()
PROXY_HOST = '0.0.0.0'
PROXY_PORT = 1298
REAL_POP3_SERVER = 'localhost'
REAL_POP3_PORT = 110
# Dictionary to map proxy users to real users
user_mapping = {
    'quintin': {
        'proxy_pass': '1235',
        'real_user': 'quintin',
        'real_pass': '1235'
    },
    'alice': {
        'proxy_pass': '1235',
        'real_user': 'alice',
        'real_pass': '1235'
    }
    # Add more users as needed
}

def log(message):
    """Log a message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    logger.info(log_message)

def handle_client(client_socket):
    try:
        # Connect to the real POP3 server
        real_socket = socket.create_connection((REAL_POP3_SERVER, REAL_POP3_PORT))
        # Optionally wrap in SSL if needed
        # real_socket = ssl.wrap_socket(real_socket)

        def send_to_real_server(command):
            real_socket.sendall(command)
            return real_socket.recv(4096)

        # Relay initial connection banner from real server to client
        client_socket.sendall(real_socket.recv(4096))

        # Authentication process
        proxy_user = None

        while True:
            client_command = client_socket.recv(4096)
            if client_command.startswith(b'USER'):
                proxy_user = client_command.split(b' ')[1].strip().decode()
                if proxy_user in user_mapping:
                    client_socket.sendall(b'+OK Proxy User accepted\r\n')
                else:
                    client_socket.sendall(b'-ERR Invalid User\r\n')
                    client_socket.close()
                    return
            elif client_command.startswith(b'PASS'):
                proxy_pass = client_command.split(b' ')[1].strip().decode()
                if proxy_user and user_mapping[proxy_user]['proxy_pass'] == proxy_pass:
                    real_user = user_mapping[proxy_user]['real_user']
                    real_pass = user_mapping[proxy_user]['real_pass']
                    # Authenticate with real server
                    real_socket.sendall(f'USER {real_user}\r\n'.encode())
                    real_socket.recv(4096)
                    real_socket.sendall(f'PASS {real_pass}\r\n'.encode())
                    real_response = real_socket.recv(4096)
                    client_socket.sendall(real_response)
                    if b'+OK' in real_response:
                        break
                    else:
                        client_socket.close()
                        return
                else:
                    client_socket.sendall(b'-ERR Invalid Pass\r\n')
                    client_socket.close()
                    return
            else:
                client_socket.sendall(b'-ERR Invalid Command\r\n')

        # Relay messages between client and real server
        while True:
            client_command = client_socket.recv(4096)
            log(f"Received from client: {client_command}")
            if not client_command:
                break
            
            # Check if the command is DELE and if the user is not 'quintin'
            if client_command.lower().startswith(b'dele') and proxy_user != 'quintin':
                client_socket.sendall(b'+OK Permission denied to be deleted.\r\n')
                log(f"Client Tried to delete but they are {proxy_user}")

            else:

                real_response = send_to_real_server(client_command)
                log(f"Received from real server: {real_response}")
                print(f"Sent to real server: {client_command}")
                # Check if the email is being retrieved
                if client_command.lower().startswith(b'retr'):

                    if b'Subject: Confidential' in real_response:
                        # Create fake email response
                        fake_subject = b'Subject: Test Email\r\n'
                        fake_body = b'We are sorry for the inconvenience, we are testing that our mail delivery works.\r\n'
                        real_response_lines = real_response.split(b'\r\n')
                        real_response_lines.insert(6, f'X-Handled-By: {proxy_user}'.encode())
                        for i, line in enumerate(real_response_lines):
                            if line.startswith(b'Subject: '):
                                real_response_lines[i] = fake_subject
                                # Insert fake body after the headers
                                real_response_lines[i + 1] = b''  # Blank line indicating end of headers
                                real_response_lines[i + 2] = fake_body
                                for j in range(i + 3, len(real_response_lines) - 2):
                                    real_response_lines[j] = b'\r\n'
                                break
                        real_response = b'\r\n'.join(real_response_lines)
                    else:
                    # Insert the 'Handled by <username>' line as a header in the email
                        real_response_lines = real_response.split(b'\r\n')
                        real_response_lines.insert(6, f'X-Handled-By: {proxy_user}'.encode())
                        real_response = b'\r\n'.join(real_response_lines)
                client_socket.sendall(real_response)


        client_socket.close()
        real_socket.close()
    except Exception as e:
        error_message = f"Error: {e}"
        log(error_message)
        client_socket.close()

def main():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(5)
    log(f"Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")
    print(f"Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")
    while True:
        client_socket, addr = proxy_socket.accept()
        log(f"Accepted connection from {addr}")
        print(f"Accepted connection from {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()
