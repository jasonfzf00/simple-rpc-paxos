from rpc_server import RPCServer

cluster = [(1,"10.128.0.2",8001),(2,"10.128.0.3",8002),(3,"10.128.0.4",8003)]
server = RPCServer(1,"localhost",8001,cluster)
server.start_server()