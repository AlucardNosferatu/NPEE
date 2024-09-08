import socket
import threading

LOCAL_IP = '192.168.110.182'
LOCAL_PORT = 25857
REMOTE_IP = '3.64.3.18'
REMOTE_PORT = 25857


def print_data(data, direction):
    """打印数据，以 TCP 包的单位逐行显示。"""
    print(f"--- {direction} ---")
    # 以换行符分隔每行
    for line in data.splitlines():
        print(line)
    print(f"--- End of {direction} ---")


def handle_client_to_remote(client_socket, remote_socket):
    while True:
        try:
            data = client_socket.recv(4096)
            if not data:
                break
            # 打印客户端到远程服务器的数据
            print_data(data.decode('utf-8', errors='ignore'), "Client to Remote")
            remote_socket.sendall(data)
        except (socket.error, ConnectionResetError):
            break
    client_socket.close()


def handle_remote_to_client(remote_socket, client_socket):
    while True:
        try:
            data = remote_socket.recv(4096)
            if not data:
                break
            # 打印远程服务器到客户端的数据
            print_data(data.decode('utf-8', errors='ignore'), "Remote to Client")
            client_socket.sendall(data)
        except (socket.error, ConnectionResetError):
            break
    remote_socket.close()


def handle_client(client_socket):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as remote_socket:
        remote_socket.connect((REMOTE_IP, REMOTE_PORT))

        client_to_remote_thread = threading.Thread(target=handle_client_to_remote, args=(client_socket, remote_socket))
        remote_to_client_thread = threading.Thread(target=handle_remote_to_client, args=(remote_socket, client_socket))

        client_to_remote_thread.start()
        remote_to_client_thread.start()

        client_to_remote_thread.join()
        remote_to_client_thread.join()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((LOCAL_IP, LOCAL_PORT))
        server_socket.listen(5)
        print(f"Listening on {LOCAL_IP}:{LOCAL_PORT}")

        while True:
            client_socket, addr = server_socket.accept()
            print(f"Accepted connection from {addr}")

            client_handler = threading.Thread(target=handle_client, args=(client_socket,))
            client_handler.start()


if __name__ == "__main__":
    main()
