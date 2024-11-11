import xmlrpc.client
import base64
import time

# Connect to the server
proxy_a = xmlrpc.client.ServerProxy("http://127.0.0.1:8001/", allow_none=True)
proxy_b = xmlrpc.client.ServerProxy("http://127.0.0.1:8002/", allow_none=True)
text_a = "message_a"
text_b = "message_b"

# proxy_a.update_value("message_a")
time.sleep(1)
