"""
Author: Jason (Zefeng) Fu
Date: 11/10/2024

Stimulates when 2 clients call update_value()

"""

import xmlrpc.client
from multiprocessing import Process
import time

def send_msg_a():
    proxy_a = xmlrpc.client.ServerProxy("http://127.0.0.1:8001/", allow_none=True)
    text_a = "message_a"
    proxy_a.update_value("message_a")


def send_msg_b():
    proxy_b = xmlrpc.client.ServerProxy("http://127.0.0.1:8002/", allow_none=True)
    text_b = "message_b"
    proxy_b.update_value("message_b")

if __name__ == "__main__":
    p1 = Process(target=send_msg_a)
    p1.start()
    time.sleep(0.5)
    p2 = Process(target=send_msg_b)
    p2.start()
    p1.join()
    p2.join()
    
