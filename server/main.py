"""
Author: Jason (Zefeng) Fu
Date: 11/10/2024

The is utility function that stimulate running 3 servers locally.

"""

from rpc_server import RPCServer
import threading
import time

def run_servers():
    clusters = [
            [(2, "localhost", 8002), (3, "localhost", 8003)],  # Cluster for server 1
            [(1, "localhost", 8001), (3, "localhost", 8003)],  # Cluster for server 2
            [(1, "localhost", 8001), (2, "localhost", 8002)]   # Cluster for server 3
        ]

    server_configs = [
        (1, "localhost", 8001, clusters[0]),
        (2, "localhost", 8002, clusters[1]),
        (3, "localhost", 8003, clusters[2])
    ]

    threads = []

    for node_id, ip, port, cluster in server_configs:
        server = RPCServer(node_id, ip, port, cluster)
        thread = threading.Thread(target=server.start_server)
        thread.daemon = True  # Allows threads to exit when main program exits
        thread.start()
        threads.append(thread)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down servers...")

if __name__ == "__main__":
    run_servers()