import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from http import HTTPStatus
# Quintin d'Hotman de Villiers u21513768
# Define the port
PORT = 55555

# Define the Fibonacci function to generate Fibonacci triples
def fibonacci(n):
    fib_list = [0, 1]
    for i in range(2, n):
        fib_list.append(fib_list[-1] + fib_list[-2])
    return fib_list

# Define the HTTP request handler class
class FibonacciRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse the request URL to extract query parameters
            url_parts = urlparse(self.path)
            query_params = parse_qs(url_parts.query)

            # Get the current index from the query parameters
            current_index = int(query_params.get('index', ['0'])[0])

            # Generate Fibonacci sequence
            fib_sequence = fibonacci(current_index + 3)

            # Set the response status code to 200 OK
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            # Start building the HTML response
            html_response = """
                <html>
                <head>
                <title>Fibonacci Triples</title>
                <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    .centered-card {
                        margin: 0 auto;
                        margin-top: 10%;
                    }
                    body {
                        height: 100vh;
                        --u: 10px;
                        --c1: #fbf9fe;
                        --c2: #02b6e7;
                        --c3: #00699b;
                        --gp: 50%/ calc(var(--u) * 16.9) calc(var(--u) * 12.8);
                        background: 
                            conic-gradient(from 122deg at 50% 85.15%, var(--c2) 0 58deg, var(--c3) 0 116deg, #fff0 0 100%) var(--gp),
                            conic-gradient(from 122deg at 50% 72.5%, var(--c1) 0 116deg, #fff0 0 100%) var(--gp),
                            conic-gradient(from 58deg at 82.85% 50%, var(--c3) 0 64deg, #fff0 0 100%) var(--gp),
                            conic-gradient(from 58deg at 66.87% 50%, var(--c1) 0 64deg, var(--c2) 0 130deg, #fff0 0 100%) var(--gp),
                            conic-gradient(from 238deg at 17.15% 50%, var(--c2) 0 64deg, #fff0 0 100%) var(--gp),
                            conic-gradient(from 172deg at 33.13% 50%, var(--c3) 0 66deg, var(--c1) 0 130deg, #fff0 0 100%) var(--gp),
                            linear-gradient(98deg, var(--c3) 0 15%, #fff0 calc(15% + 1px) 100%) var(--gp),
                            linear-gradient(-98deg, var(--c2) 0 15%, #fff0 calc(15% + 1px) 100%) var(--gp),
                            conic-gradient(from -58deg at 50.25% 14.85%, var(--c3) 0 58deg, var(--c2) 0 116deg, #fff0 0 100%) var(--gp),
                            conic-gradient(from -58deg at 50% 28.125%, var(--c1) 0 116deg, #fff0 0 100%) var(--gp),
                            linear-gradient(90deg, var(--c2) 0 50%, var(--c3) 0 100%) var(--gp);
                    }

                    p {
                        margin: 0;
                    }
                </style>
                </head>
                <body>
            """

            # Log request data into the browser's console using JavaScript
            client_address = str(self.client_address[0])  # Only take the IP address
            # request_line = self.requestline

            # Format the request data according to HTTP RFC
            http_request_data = f"{self.command} {self.path} {self.request_version}"
            html_response += f"<script>console.log('Request received: {http_request_data} - {client_address}');</script>" # Gun in mouth type goofy ahhh line

            html_response += """
            <div class="container">
                <div class="row">
                <div class="col-md-6 mx-auto">
                    <div class="card centered-card">
                    <div class="card-body"><h1 class="card-title display-3">Fibonacci Triples</h1>
            """

            # Add Fibonacci numbers to the HTML response
            html_response += "<ul class='list-group'>"
            for i, fib_num in enumerate(fib_sequence[current_index:current_index + 3], start=current_index):
                if i % 2 == 0:  # Check if the index is even
                    html_response += f"<li class='list-group-item d-flex justify-content-between align-items-center border-0 list-group-item-dark'>{fib_num}<span class='badge badge-primary badge-pill'>{i}</span></li>"
                else:
                    html_response += f"<li class='list-group-item d-flex justify-content-between align-items-center border-0'>{fib_num}<span class='badge badge-primary badge-pill'>{i}</span></li>"
                
            html_response += "</ul><br/>"

            # Add navigation buttons
            if current_index > 0:
                html_response += f"<a href='/?index={current_index - 1}' class='btn btn-outline-danger'>Previous</a> "
            else:
                html_response += "<p class='btn btn-danger disabled'>Previous</p> "
            html_response += f"<a href='/?index={current_index + 1}' class='btn btn-outline-primary'>Next</a>"

            # End the HTML response
            html_response += """
                        </div>
                    </div>
                </div>
                </div>
            </div></body></html>"""

            # Send the HTML response to the client
            self.wfile.write(html_response.encode('utf-8'))
            

        except Exception as e:
            # If an error occurs, send an appropriate error response
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, message="Internal Server Error", explain=str(e))

    def send_error(self, code, message=None, explain=None):
        # Override send_error to provide custom error pages
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(f"<html><head><title>Error {code}</title></head><body><h1>Error {code}</h1><p>{message}</p></body></html>".encode('utf-8'))

# Create an HTTP server instance with the custom request handler
with socketserver.TCPServer(("", PORT), FibonacciRequestHandler) as httpd:
    print(f"Server running on port {PORT}")
    # Keep the server running until interrupted
    httpd.serve_forever()
