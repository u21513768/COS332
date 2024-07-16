import socket

def send_request(request, server):
    server.sendall(request.encode())

def receive_response(server):
    response = server.recv(4096).decode()
    return response

def main():
    # Connect to the LDAP server
    ldap_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ldap_server.connect(('192.168.3.102', 389))

    # Ask for the organization name from the user
    org_name = input("Enter the organization name: ")

    # Construct LDAP search query
    ldap_query = "(o={})".format(org_name)

    # Construct LDAP request
    ldap_request = (
        "ldapsearch -x -H ldap:// -b dc=za,dc=com -D cn=admin,dc=za,dc=com -W"
        " -LLL -z 1 {}".format(ldap_query)
    )

    # Send LDAP request to the server
    send_request(ldap_request, ldap_server)

    # Receive and interpret the response from the server
    ldap_response = receive_response(ldap_server)
    print(ldap_response)

    # Close the connection
    ldap_server.close()

if __name__ == "__main__":
    main()
