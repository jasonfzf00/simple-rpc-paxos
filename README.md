# Simple XMLRPC Paxos
## Overview
This project implements a basic Paxos consensus algorithm using the `xmlrpc` package in Python. The system consists of multiple distributed nodes, each running an instance of the `RPCServer` class, which communicate with each other to achieve consensus over shared data. 

## Requirements

- Python 3.8+

## Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/paxos-xmlrpc.git
   cd paxos-xmlrpc
   ``` 
2. **Run Servers**:
In server directory, the `main.py` file provides a simple cluster setup that runs locally.
   ```bash
   cd paxos-xmlrpc/server
   python main.py
   ``` 
3. **Run Client**:
In client directory, the `rpc_client.py` provides example of two clients calls `update_value()` to two different server.
   ```bash
   cd paxos-xmlrpc/client
   python rpc_client.py
   ``` 