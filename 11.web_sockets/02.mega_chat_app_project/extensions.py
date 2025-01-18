import socketio

# Initialize the Socket.IO server with CORS settings
socket = socketio.AsyncServer(
    cors_allowed_origins=["http://localhost:5173"],  # Explicitly allow your frontend origin
    async_mode='asgi',
    
)
socket_app = socketio.ASGIApp(socket)
