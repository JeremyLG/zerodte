import os

import paramiko

# Read the .env file and populate environment variables
with open(".env", "r") as file:
    for line in file:
        key, value = line.strip().split("=")
        os.environ[key] = value

# Access environment variables
hostname = os.getenv("HOSTNAME")
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
port = 22

# Path to the file on the remote server
remote_path = rf"C:\Users\{username}\AppData\Local\Packages\TradeAutomationToolbox_f46cr67q31chc\LocalState\data.db3"
# Local destination path
local_path = "data/tat/data.db3"

# Create an SSH client
client = paramiko.SSHClient()
client.load_system_host_keys()

# Connect to the remote server
client.connect(hostname, port, username, password)

# Create an SFTP client session
sftp = client.open_sftp()

# Download the file from the remote server
sftp.get(remote_path, local_path)

# Close the SFTP session and SSH connection
sftp.close()
client.close()
