from .extensions import socket

@socket.on("connect")
async def connect(sid, env):
    print(f"client connected {str(sid)}")

@socket.on("disconnect")
async def disconnect(sid):
    print(f"client dis-connected {str(sid)}")
