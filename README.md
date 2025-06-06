Quick description:
A CLI virtual machine manager was created by myself during 8th grade.

Key points: 
- Utilized socket programming to create a server where virtual machines can connect to
- The server serves as an access point for the user to manage all connected machines
- SQLite3 to store VM info
- Has built-in file transfer capabilities

How to run server.py: 
- Run the server.py file via "python3 server.py"
- It will try to download the dependency Funcy
- A new database will be initiated
- You can edit the server props by editing the code

How to run connect.py: 
- python3 client.py <server ip> <server port> <server password> <root password>
- Explanatory, nothing else is needed
