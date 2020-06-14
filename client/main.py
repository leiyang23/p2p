import socket
import time


def serve(host, port, retry=3):
    for i in range(retry):
        try:
            sock_to_server = socket.socket()
            sock_to_server.connect((host, port))

            while True:
                data = b""
                while True:
                    buf = sock_to_server.recv(1000)
                    data += buf
                    if len(buf) < 1000:
                        break

                sock_to_local = socket.socket()
                sock_to_local.connect(("localhost", 80))
                sock_to_local.sendall(data)

                data = b""
                while True:
                    buf = sock_to_local.recv(1000)
                    data += buf
                    if len(buf) < 1000:
                        sock_to_local.close()
                        break
                print(data)
                sock_to_server.sendall(data)
                time.sleep(.1)
        except Exception as e:
            pass

    raise ValueError("Can't connect to server, max retry exceeded.")


if __name__ == '__main__':
    import sys

    host = "47.111.175.222"
    port = 8000

    if len(sys.argv) > 1:
        host = sys.argv[1]
        port = sys.argv[2]

    serve(host, port)
