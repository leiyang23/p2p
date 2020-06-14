import socket
from selectors import DefaultSelector, EVENT_READ

client_conn = None
sel = DefaultSelector()
Template_Server_Error = b'HTTP/1.1 500 \r\nContent-Type: text/plain\r\n\r\nProxy Server error\r\n'
Template_No_Client = b'HTTP/1.1 501 \r\nContent-Type: text/plain\r\n\r\nNo Client Exists\r\n'


def accept(sock: socket.socket, mask):
    global client_conn

    conn, addr = sock.accept()

    if "127.0.0.1" in addr:
        sel.register(conn, EVENT_READ, data=read_from_proxy)
        conn.setblocking(False)
    else:
        client_conn = conn
        client_conn.setblocking(True)


def read_from_proxy(conn: socket.socket, mask):
    global client_conn
    try:
        while True:
            buf = conn.recv(1000)
            client_conn.send(buf)
            if len(buf) < 1000:
                break

        # 将结果一次性返回给nginx
        data = b""
        while True:
            buf = client_conn.recv(1000)
            data += buf
            if len(buf) < 1000:
                break
        conn.sendall(data)

    except AttributeError:
        conn.sendall(Template_No_Client)

    except ConnectionResetError:
        client_conn = None
        conn.sendall(Template_No_Client)

    except (ConnectionAbortedError,):
        conn.sendall(Template_Server_Error)

    finally:
        sel.unregister(conn)
        conn.close()


sock_server = socket.socket()
sock_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 断开后释放端口
sock_server.bind(("0.0.0.0", 8000))
sock_server.listen(20)
sock_server.setblocking(False)
sel.register(sock_server, EVENT_READ, data=accept)

try:
    while True:
        events = sel.select(timeout=30)
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
except KeyboardInterrupt:
    sock_server.close()
finally:
    sock_server.close()
