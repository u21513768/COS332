import re
import socket

def extract_message_id(email_content):
    try:
        # Convert email content to string
        email_str = email_content.decode()
        # Split the email content into lines
        lines = email_str.split('\n')
        # Flag to track if BCC header is detected
        bcc_detected = False
        email_found = False
        email_warning = False
        fake_email_warning = False

        for line in lines:
            # Check if the line contains the "BCC:" header
            if line.lower().startswith("bcc:"):
                bcc_detected = True
                print("BCC Found")
                break
            elif (line.lower().startswith("to:") or line.lower().startswith("cc:")) and "quintin@milk.com" in line.lower():
                email_found = True
                print("Email found")
                break
            elif "subject: [bcc warning]" in line.lower():
                email_warning = True
            elif line.lower().startswith("from:"):
                if "test@milk.com" in line.lower():
                    email_warning = True
                else:
                    email_warning = False
                    fake_email_warning = True

        if (not email_found):
            bcc_detected = True
        if email_warning and not fake_email_warning:
            bcc_detected = False
            print("Skipping BCC warning.")
        
        return bcc_detected
    except Exception as e:
        print("Error extracting BCC header:", e)
        return False

def send_warning_email(message_id):
    try:
        print("Sending warning email...")
        # Define SMTP server details
        server_host = 'localhost'
        server_port = 25
        sender_email = 'test@milk.com'
        sender_domain = 'milk.com'
        recipient_email = 'quintin@milk.com'

        # Prepare email content
        subject = "[BCC Warning] Potential BCC Email"
        body = "You received a (possible) BCC email with Message-Id: " + message_id + " \nPlease be cautious. \n\n This is a warning email, please do not respond to this."

        # Establish connection to SMTP server
        smtp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        smtp_socket.connect((server_host, server_port))

        # Send email
        smtp_socket.sendall(f"HELO {sender_domain}\r\n".encode())
        smtp_socket.sendall(f"MAIL FROM: <{sender_email}>\r\n".encode())
        smtp_socket.sendall(f"RCPT TO: <{recipient_email}>\r\n".encode())
        # Include the recipient's email address in the "To:" header
        smtp_socket.sendall("DATA\r\n".encode())
        smtp_socket.sendall(f"Subject: {subject}\r\n".encode())
        smtp_socket.sendall("\r\n".encode())
        smtp_socket.sendall(f"{body}\r\n.\r\n".encode())

        # Read response from server
        response = smtp_socket.recv(1024)
        print("Response from server:", response.decode())

        # Close connection
        smtp_socket.sendall("QUIT\r\n".encode())
        smtp_socket.close()
        print("Warning email sent successfully.")
    except Exception as e:
        print("Error sending warning email:", e)


def retrieve_emails(pop3_socket):
    try:
        emails = []
        # Send LIST command to get the list of messages
        pop3_socket.send(b'LIST\r\n')
        response = pop3_socket.recv(1024).decode()
        print("Response from POP3 server after LIST:", response)

        # Parse the response to determine the number of messages
        num_messages = int(response.split()[1])
        print("Number of messages:", num_messages)

        # Iterate over each message
        for i in range(1, num_messages + 1):
            # Send RETR command to retrieve each message
            pop3_socket.send(f'RETR {i}\r\n'.encode())
            email_content = b""
            # Keep reading until the end of the message is reached
            while True:
                response = pop3_socket.recv(1024)
                email_content += response
                if response.endswith(b"\r\n.\r\n"):
                    break
            print("Retrieved email", i)
            emails.append(email_content)
        return emails
    except Exception as e:
        print("Error retrieving emails:", e)
        return []

def monitor_pop3():
    try:
        # Connect to POP3 server
        pop3_server = 'localhost'
        pop3_port = 110
        pop3_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pop3_socket.connect((pop3_server, pop3_port))

        # Authenticate
        pop3_socket.send(b'USER quintin\r\n')
        response = pop3_socket.recv(1024)
        print("Response from POP3 server after USER:", response.decode())
        pop3_socket.send(b'PASS 1235\r\n')  # Replace with your actual password
        response = pop3_socket.recv(1024)
        print("Response from POP3 server after PASS:", response.decode())

        # Retrieve emails
        emails = retrieve_emails(pop3_socket)
        print("Total emails retrieved:", len(emails))

        # Check for BCC header and send warning email if detected in each email
        for email_content in emails:
            if extract_message_id(email_content):
                # Get the Message-Id
                message_id = re.search(r"Message-Id: <(.*?)>", email_content.decode()).group(1)
                # Check if the Message-Id has been flagged before
                if not is_already_flagged(message_id):
                    # Store the Message-Id in the flagged file
                    store_flagged_message(message_id)
                    send_warning_email(message_id)
                else:
                    print("Duplicate BCC warning avoided.")
            else:
                print("No BCC header found in the email.")

        # Close connection
        pop3_socket.send(b'QUIT\r\n')
        pop3_socket.close()
    except Exception as e:
        print("Error monitoring POP3 server:", e)

def is_already_flagged(message_id):
    try:
        # print(message_id)
        with open("flagged_emails.txt", "r") as file:
            flagged_emails = file.readlines()
            # print(flagged_emails)
            # Strip whitespace characters from each line
            flagged_emails = [email.strip() for email in flagged_emails]
            if message_id in flagged_emails:
                return True
        return False
    except Exception as e:
        print("Error checking flagged emails:", e)
        return False


def store_flagged_message(message_id):
    try:
        with open("flagged_emails.txt", "a") as file:
            file.write(message_id + "\n")
    except Exception as e:
        print("Error storing flagged message:", e)

# Call the function to monitor the POP3 server
monitor_pop3()
