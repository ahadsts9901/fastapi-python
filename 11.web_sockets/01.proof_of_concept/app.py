import socketio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# Create a FastAPI app and a Socket.IO server
app = FastAPI()

# Create Socket.IO server
sio = socketio.AsyncServer()
socket_app = socketio.ASGIApp(sio)

# Serve static files (e.g., HTML)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def index():
    # Serve the index.html file
    with open("static/index.html", "r") as f:
        content = f.read()
    return HTMLResponse(content=content)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def message(sid, data):
    print(f"Message received from {sid}: {data}")
    # Emit the received message to all connected clients
    await sio.emit('message', f"Message received: {data}")

# Mount the Socket.IO app correctly
app.mount("/ws", socket_app)

# Run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# uvicorn app:app --reload ====> like nodemon in nodejs
