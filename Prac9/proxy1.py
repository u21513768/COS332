import socket
import ssl
# multiple users but all can delete
# Configuration
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
            if not client_command:
                break
            print(client_command)
            real_response = send_to_real_server(client_command)
            client_socket.sendall(real_response)

        client_socket.close()
        real_socket.close()
    except Exception as e:
        print(f"Error: {e}")
        client_socket.close()

def main():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(5)
    print(f"Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        client_socket, addr = proxy_socket.accept()
        print(f"Accepted connection from {addr}")
        handle_client(client_socket)

if __name__ == "__main__":
    main()
