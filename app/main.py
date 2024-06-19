import socket
import os
import sys
import pprint
import asyncio
import gzip
from concurrent.futures import ThreadPoolExecutor as th
from collections import defaultdict

CRLF = b"\r\n"
ENCODING = "ISO-8859-1"

statuses = {
    200: "OK",
    404: "Not Found",
    201: "Created",
}

def get_request(sock):
    try:
        data = bytearray()
        while True:
            buffer = bytearray(256)
            sock.recv_into(buffer, 256)
            data += buffer.replace(b"\x00", b"")
            if buffer.find(CRLF + CRLF) != -1:
                break
        req_message, body = data.split(CRLF + CRLF)
        data = [tuple(x.decode(ENCODING).split(": ")) for x in req_message.split(CRLF)]
        req = defaultdict(str)
        req["request_line"] = {
            k: v for k, v in zip(["method", "path", "version"], data[0][0].split(" "))
        }
        req["headers"] = {x[0]: x[1] for x in data[1:]}
        if "Content-Length" in req["headers"].keys():
            length = req["headers"]["Content-Length"] = int(
                req["headers"]["Content-Length"]
            )
            if length > len(body):
                to_recv = length - len(body)
                chunk_size = 512
                while to_recv > 0:
                    size = min(chunk_size, to_recv)
                    buffer = bytearray(size)
                    sock.recv_into(buffer, size)
                    to_recv -= size
                    body += buffer
        req["body"] = body.decode(ENCODING)
    except Exception as e:
        print(e)
    return req

def check_encoding(request_headers: dict, response_headers: dict):
    try:
        validated_encodings = []
        if "Accept-Encoding" not in request_headers:
            return
        for encoding in request_headers["Accept-Encoding"].split(", "):
            if encoding in [
                "gzip",
            ]:
                validated_encodings.append(encoding)
        response_headers["Content-Encoding"] = ",".join(x for x in validated_encodings)
        return validated_encodings
    except Exception as e:
        print(e)
        
def compress(type, data):
    if type:
        type = type[0]
    else:
        return data.encode(ENCODING)
    if type == "gzip":
        if isinstance(data, bytes):
            return gzip.compress(data)
        if isinstance(data, str):
            return gzip.compress(data.encode(ENCODING))

def response(status=404, headers={}):
    response = f"HTTP/1.1 {status} {statuses[status]}\r\n"
    for key, value in headers.items():
        response += f"{key}: {value}\r\n"
    response += "\r\n"
    return response.encode()

def end_point_echo(sock, request):
    body = request["request_line"]["path"].split("/echo/")[1]
    
    headers = {
        "Content-Type": "text/plain",
    }
    try:
        encoding = check_encoding(request["headers"], headers)
        body = compress(encoding, body)
        headers["Content-Length"] = len(body)
        data = response(200, headers)
        sock.send(data + body)
    except Exception as e:
        print(e)
    
def end_point_blank(sock):
    sock.send(
        response(
            200,
            {
                "Content-Length": 0,
                "Content-Type": "text/plain",
            },
        )   
    )
    
def end_point_path(sock, request):
    body = request["request_line"]["path"].strip("/")
    headers = {
        "Content-Type": "text/plain",
    }
    encoding = check_encoding(request["headers"], headers)
    body = compress(encoding, body)
    headers["Content-Length"] = len(body)
    sock.send(response(404, headers) + body)

def end_point_user_agent(sock, request):
    body = request["headers"]["User-Agent"]
    sock.send(
        response(
            200,
            {
                "Content-Length": len(body),
                "Content-Type": "text/plain",
            },
        )
        + body.encode(ENCODING)
    )
    
def end_point_file(sock, request):
    parent = sys.argv[2]
    file_name = request["request_line"]["path"].split("/files/")[1]
    file_path = os.path.join(parent, file_name)
    if os.path.exists(file_path):
        with open(file_path, "rt") as f:
            body = f.read()
        headers = {
            "Content-Type": "application/octet-stream",
        }
        encoding = check_encoding(request["headers"], headers)
        body = compress(encoding, body)
        headers["Content-Length"] = len(body)
        resp = response(200, headers)
        print(f"{resp=}")
        sock.send(resp + body)
    else:
        resp = response()
        sock.send(resp)

def create_file(sock: socket.socket, request: dict):
    parent = sys.argv[2]
    file_name = request["request_line"]["path"].split("/files/")[1]
    file_path = os.path.join(parent, file_name)
    with open(file_path, "xt") as f:
        f.write(request["body"])
    sock.send(response(201, {}))
    
def handler(c_sock, addr):
    print("connection from ", addr)
    request = get_request(c_sock)
    print(f"{request=}")
    
    try:
        if request["request_line"]["method"] == "POST":
            create_file(c_sock, request)
            return
    except Exception as e:
        print(e)
        
    path = request["request_line"]["path"]
    
    if "echo" in path:
        end_point_echo(c_sock, request)
        
    elif path == "/":
        end_point_blank(c_sock)
        
    elif "user-agent" in path:
        end_point_user_agent(c_sock, request)
    
    elif "files" in path:
        try:
            end_point_file(c_sock, request)
        except Exception as e:
            print(e)
        
    else:
        end_point_path(c_sock, request)

def main():
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    executor = th()
    while True:
        executor.submit(handler, *server_socket.accept())

if __name__ == "__main__":
    main()
