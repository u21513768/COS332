# smtp_proxy.py
import socket
import threading

# Configuration
PROXY_HOST = '0.0.0.0'
PROXY_PORT = 1300
REAL_SMTP_SERVER = 'localhost'
REAL_SMTP_PORT = 25

def handle_client(client_socket):
    try:
        # Connect to the real SMTP server
        real_socket = socket.create_connection((REAL_SMTP_SERVER, REAL_SMTP_PORT))

        def relay_message(src_socket, dst_socket):
            try:
                while True:
                    message = src_socket.recv(4096)
                    if not message:
                        break
                    dst_socket.sendall(message)
            except Exception as e:
                print(f"Error during relaying message: {e}")
            finally:
                src_socket.close()
                dst_socket.close()

        # Create threads to relay messages in both directions
        client_to_server_thread = threading.Thread(target=relay_message, args=(client_socket, real_socket))
        server_to_client_thread = threading.Thread(target=relay_message, args=(real_socket, client_socket))

        client_to_server_thread.start()
        server_to_client_thread.start()

        client_to_server_thread.join()
        server_to_client_thread.join()

    except Exception as e:
        print(f"Error handling client: {e}")
        client_socket.close()

def main():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(5)
    print(f"SMTP Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")

    while True:
        client_socket, addr = proxy_socket.accept()
        print(f"Accepted connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

if __name__ == "__main__":
    main()
