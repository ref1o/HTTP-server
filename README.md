# HTTP-server
## Description
This project is a simple HTTP server implemented in Python. It handles various types of HTTP requests, including GET and POST, and supports functionalities like echoing request data, serving files, handling user-agent requests, and more. The server also supports gzip compression for responses.
## Directory Structure
```
.
├── app
│   └── main.py
└── run_server.sh
```
## Files
### main.py
The main script of the HTTP server located in `app/main.py`. It includes the following functionalities:

- Handles incoming HTTP requests and parses them.
- Supports endpoints for echoing, blank responses, user-agent, serving files, and creating files.
- Supports gzip compression for responses if requested by the client.
- Multithreaded handling of client connections.
### run_server.sh
A shell script to run the HTTP server using `pipenv`.
## Endpoints
- `/`: Returns a blank response.
- `/echo/{message}`: Echoes the `{message}` part of the URL.
- `/user-agent`: Returns the user-agent header sent by the client.
- `/files/{filename}`: Serves the file `{filename}` if it exists in the specified directory.
- POST `/files/{filename}`: Creates a new file `{filename}` with the body of the request as its content.
## Setup and Usage
### Prerequisites
- Python 3.x
- pipenv
### Installation
1. Clone the repository:
```bash
git clone https://github.com/ref1o/HTTP-server.git
cd HTTP-server   
```

2. Install dependencies:
```bash
pipenv install  
```
### Running the Server
1. Run the server using the provided shell script:
```bash
./run_server.sh /path/to/files/directory  
```
The server will start on `localhost` at port `4221`.
### Example Requests
- To get a blank response:
```bash
curl http://localhost:4221/
```
- To escho a message:
```bash
curl http://localhost:4221/echo/hello
```
- To get the user-agent:
```bash
curl http://localhost:4221/user-agent
```
- To retrieve a file:
```bash
curl http://localhost:4221/files/filename.txt
```
- To create a new file:
```bash
curl -X POST -d "file content" http://localhost:4221/files/filename.txt
```

## Code Overview
### Imports and Costants
The script imports various modules and sets up some constants:
- `socket`, `os`, `sys`, `pprint`, `asyncio`, `gzip`, `concurrent.futures.ThreadPoolExecutor`, `collections.defaultdict`
- Constants: `CRLF`, `ENCODING`, `statuses`
### Functions
- `get_request(sock)`: Reads and parses the incoming HTTP request.
- `check_encoding(request_headers, response_headers)`: Checks and validates encoding from the request headers.
- `compress(type, data)`: Compresses the response data if needed.
- `response(status, headers)`: Constructs an HTTP response.
- `end_point_echo(sock, request)`: Handles the echo endpoint.
- `end_point_blank(sock)`: Handles the root endpoint returning a blank response.
- `end_point_path(sock, request)`: Handles requests to non-existent paths.
- `end_point_user_agent(sock, request)`: Handles the user-agent endpoint.
- `end_point_file(sock, request)`: Serves files from the specified directory.
- `create_file(sock, request)`: Creates a file with the content from the request body.
- `handler(c_sock, addr)`: Main handler for incoming client connections.
- `main()`: Main function to set up the server and handle connections using threads.

## License
This project is licensed under the MIT License.
