"""
Author: Jason (Zefeng) Fu
Date: 

The server class uses xmlrpc package and provides
implmentation of basic paxos algorithm.

"""

from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from datetime import datetime
import sys
import os
import base64
import random
import time
from typing import List, Tuple

class RPCServer:

    def __init__(self, node_id: int, ip: str, port: int, cluster: List[Tuple[int, str, int]]):
        # Log file to check output and debug
        self.node_id = node_id
        self.cluster = cluster
        self.promised_number = 0.0 + (node_id / 10)
        self.accepted_number = self.promised_number
        self.accepted_data = None # If not previously accepted this will be None
        self.quorum = (len(self.cluster) + 1) // 2 + 1
        self.server = SimpleXMLRPCServer((ip, port), allow_none=True)
        self.server.register_instance(self)
        file_dir = f"node{self.node_id}"
        os.makedirs(file_dir, exist_ok=True)
        self.log_path = os.path.join(file_dir,f"node{self.node_id}_log")
        self.file_path = os.path.join(file_dir,"CISC5597")
        with open(self.log_path, "w") as file:
            file.write("")
        with open(self.file_path, "wb") as file:
            file.write(base64.b64decode(base64.b64encode(b"Initialized")))
        self.write_log(f"Server {node_id} listening on {ip}:{port}")
    
    def start_server(self):
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.write_log("\nExiting...")
            sys.exit(0)
    
    # Encode file in Base64 for XML-RPC file transfer
    def read_file_data(self):
        with open(self.file_path, "rb") as file:
            file_data = base64.b64encode(file.read()).decode("utf-8")
        return file_data
    
    # Call to generate random delay
    def random_delay(self):
        delay = random.uniform(1, 3)
        time.sleep(delay)

    # Decode the base64 encoded file data and write to file
    def write_file_data(self, file_data):
        try:
            decoded_data = base64.b64decode(file_data)
            with open(self.file_path, "wb") as file:
                file.write(decoded_data)
        except base64.binascii.Error:
            print("Error: The provided file data is not valid Base64.")
        except Exception as e:
            print(f"Exception occurred: {repr(e)}")

    # Print log info and write to log file
    def write_log(self, msg):
        print(msg)
        with open(self.log_path, "a") as file:
            file.write(datetime.now().strftime("%m/%d/%Y %H:%M:%S")+": "+msg+"\n")

    # Proposal Phase
    # Invoke RPC calls prepare() on other nodes within the cluster.
    def propose(self):
        attempts = 0
        max_attempts = 10
        returned_accepted_number = 0.0
        while attempts < max_attempts:
            self.promised_number += 1
            self.accepted_number = self.promised_number
            vote = 1
            for node_id, ip, port in self.cluster:
                url = f"http://{ip}:{port}"
                try:
                    proxy = ServerProxy(url)
                    res = proxy.prepare(self.promised_number)
                    # Accept proposal?
                    if res[0]:
                        vote += 1
                    # Replace accepted_data with returned data with highest accepted number
                    if res[2] and res[1] > returned_accepted_number:
                        returned_accepted_number = res[1]
                        self.accepted_data = res[2]
                except Exception as e:
                    self.write_log(e)
                    return

            if vote >= self.quorum:
                # print("vote: "+ str(vote) +"; quorum: "+ str(self.quorum))
                self.write_log("Prepare-phase success! Trying accept-phase...")
                return True
            else:
                self.write_log(
                    "Failed to reach majority acceptance. Trying to propose again...")
                attempts +=1
        return False

    # Handle the prepare request.
    # Return Tuple(OK, highest_accepted_number, accepted_data)
    def prepare(self, proposal_number):
        if proposal_number > self.promised_number:
            self.promised_number = proposal_number
            return True, self.accepted_number, self.accepted_data
        else:
            return False, self.accepted_number, self.accepted_data

    # Accept Phase
    # Send accept request to cluster.
    def request_accept(self):
        vote = 1
        for node_id, ip, port in self.cluster:
            url = f"http://{ip}:{port}"
            try:
                proxy = ServerProxy(url)
                res = proxy.accept(self.promised_number, self.accepted_data)
                # Ok?
                if res:
                    vote += 1
            except Exception as e:
                self.write_log(f"Exception occurred: {repr(e)}")
                return
        if vote >= self.quorum:
            return True
        else:
            return False

    # Handle the accept request. Return boolean
    def accept(self, proposal_number, file_data):
        if proposal_number >= self.promised_number:
            self.promised_number = proposal_number
            self.accepted_number = proposal_number
            self.accepted_data = file_data
            return True
        else:
            return False

    # Commit changes and broadcast
    def commit(self, file_data):
        self.write_file_data(file_data)
        for node_id, ip, port in self.cluster:
            url = f"http://{ip}:{port}"
            try:
                proxy = ServerProxy(url)
                proxy.write_file_data(file_data)
            except Exception as e:
                self.write_log(f"Node{node_id} exception occurred: {repr(e)}")
            
    def update_value(self, val):
        encoded_val = base64.b64encode(val.encode("utf-8")).decode("utf-8")
        self.accepted_data = encoded_val
        if self.propose():
            # Adding max attempts to avoid infinite loop
            attempts = 0
            max_attempts = 5
            while attempts < max_attempts and not self.request_accept():
                self.propose()
                attempts += 1
            if attempts < max_attempts:
                self.commit(self.accepted_data)
                return "Success!"
            else:
                self.write_log("Failed to update value after maximum attempts.")
                return "Failed"