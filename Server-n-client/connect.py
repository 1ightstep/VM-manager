import socket, time, threading, datetime
import os, subprocess
import sys, string, random
try:
    import funcy
except:
    os.system("pip install funcy")
class client:
    def __init__(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_ip = sys.argv[1]
            self.server_port = sys.argv[2]
            self.server_password = sys.argv[3]
            self.client_root = sys.argv[4]
            self.encoding = "latin-1"
            if "-h" in sys.argv or "--help" sys.argv:
                print("python3 client.py <server ip> <server port> <server password> <root password>")
                quit()
            try:
                self.s.connect((self.server_ip, int(self.server_port)))
                self.s.send(self.server_password.encode(self.encoding))
                time.sleep(1)
                self.s.send(self.client_root.encode(self.encoding))
            except Exception as e:
                exit(f"Exited with exception: {e}")
        except IndexError as ie:
            print("python3 client.py <server ip> <server port> <server password> <root password>")
            quit()
    def manage(self):
        while True:
            command = self.s.recv(1024*100).decode(self.encoding)
            split_command = command.split("__SPACE__")
            if split_command[0] == "fetch":
                if os.path.exists(split_command[1]):
                    self.s.send("__FILE_EXISTS__".encode(self.encoding))
                    time.sleep(0.1)
                    with open(split_command[1], "rb") as f:
                        file_byte = f.read()
                        chunks = list(funcy.chunks(10, file_byte))
                        for chunk in chunks:
                            self.s.send(chunk)
                        self.s.send(b"__EOFL__")
                        f.close()
                else:
                    self.s.send(b"__NO_FILE__")
            if split_command[0] == "send":
                path = f'{split_command[1].replace(".", "")}_{"".join(random.choice(string.ascii_lowercase) for i in range(5))}'
                os.mkdir(path)
                with open(f"{path}/{split_command[1]}", "wb") as f:
                    recv_data = b'<BYTE>'
                    byte_array = []
                    while True:
                        recv_data = self.s.recv(1024)
                        if b'__EOFL__' in recv_data:
                            byte_array.append(recv_data.replace(b'__EOFL__', b''))
                            break
                        else:
                            byte_array.append(recv_data)
                            print(recv_data, end="")
                    f.write(b''.join(byte_array))
                    f.close()
            if split_command[0] == "execute":
                output = subprocess.getoutput(split_command[1])
                if output != "":
                    for char in output:
                        self.s.send(char.encode(self.encoding))
                    self.s.send("__EOFL__".encode(self.encoding))
                else:
                    self.s.send("Empty Output".encode(self.encoding))
client = client()
client.manage()
