from rpc_server import RPCServer

cluster = []
server = RPCServer(1,"localhost",8001,cluster)
server.start_server()