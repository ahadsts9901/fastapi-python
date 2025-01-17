from fastapi import FastAPI, HTTPException, Query, Body
from typing import List, Optional

app = FastAPI()

# In-memory storage
todos = []
next_id = 1


# Create a Todo
@app.post("/api/v1/todos")
def create_todo(todo= Body(...)):
    global todos, next_id
    if not todo["title"].strip():
        raise HTTPException(status_code=400, detail="Title is required and cannot be empty")
    new_todo = {
        "title": todo["title"],
        "id": next_id,
        "completed": todo["completed"] if todo["completed"] is not None else False
    }
    todos.append(new_todo)
    next_id += 1
    return {
        "message": "todo created",
        "data": new_todo
    }


# Get all Todos with optional filtering
@app.get("/api/v1/todos")
def get_todos(completed: Optional[bool] = Query(None)):
    if completed is not None:
        filtered_todos = [todo for todo in todos if todo["completed"] == completed]
        return {
            "message": "todos fetched",
            "data": filtered_todos
        }
    
    return {
        "message": "todos fetched",
        "data": todos
    }


# Get a single Todo by ID
@app.get("/api/v1/todos/{todo_id}")
def get_todo(todo_id: int):
    todo = next((todo for todo in todos if todo["id"] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    return {
        "message": "todo fetched",
        "data": todo
    }


# Update a Todo by ID
@app.put("/api/v1/todos/{todo_id}")
def update_todo(todo_id: int, updated_todo = Body(...)):
    global todos
    todo = next((todo for todo in todos if todo["id"] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    if not updated_todo["title"].strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    
    todo["title"] = updated_todo["title"]
    todo["completed"] = updated_todo["completed"]
    return {
        "message": "todo updated",
        "data": todo
    }


# Delete a Todo by ID
@app.delete("/api/v1/todos/{todo_id}")
def delete_todo(todo_id: int):
    global todos
    todo = next((todo for todo in todos if todo["id"] == todo_id), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="todo not found")
    
    todos = [todo for todo in todos if todo["id"] != todo_id]
    return {"message": "todo deleted"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
