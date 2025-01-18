import os
from fastapi import FastAPI, HTTPException, Query, Body
from typing import Optional, List
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# MongoDB connection
mongo_url = os.getenv("MONGO_URI")
if not mongo_url:
    raise ValueError("MONGO_URI environment variable not set")

client = MongoClient(mongo_url)
db = client["fastapi-mongodb-crud"]
todo_collection = db["todos"]

# Helper function to format MongoDB documents
def format_todo(todo):
    return {
        "_id": str(todo["_id"]),
        "title": todo["title"],
        "completed": todo["completed"],
        "created_at": todo["created_at"],
        "updated_at": todo["updated_at"],
    }

# Create a todo
@app.post("/api/v1/todos")
def create_todo(todo=Body(...)):
    if not todo.get("title", "").strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    new_todo = {
        "title": todo["title"],
        "completed": todo.get("completed", False),
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }
    result = todo_collection.insert_one(new_todo)
    new_todo["_id"] = str(result.inserted_id)
    return {"message": "todo created", "data": new_todo}

# Get all todos with optional filtering
@app.get("/api/v1/todos")
def get_todos(
    completed: Optional[bool] = Query(None),
    title: Optional[str] = Query(None),
):
    query = {}
    if completed is not None:
        query["completed"] = completed
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    todos = todo_collection.find(query)
    print("todos")
    print(todos)
    formatted_todos = [format_todo(todo) for todo in todos]
    return {"message": "todos fetched", "data": formatted_todos}

# Get a single todo by ID
@app.get("/api/v1/todos/{todo_id}")
def get_todo(todo_id: str):
    try:
        todo = todo_collection.find_one({"_id": ObjectId(todo_id)})
    except:
        raise HTTPException(status_code=400, detail="invalid todo ID")
    if not todo:
        raise HTTPException(status_code=404, detail="todo not found")
    return {"message": "todo fetched", "data": format_todo(todo)}

# Update a todo by ID
@app.put("/api/v1/todos/{todo_id}")
def update_todo(todo_id: str, updated_todo=Body(...)):
    try:
        todo = todo_collection.find_one({"_id": ObjectId(todo_id)})
    except:
        raise HTTPException(status_code=400, detail="invalid todo ID")
    if not todo:
        raise HTTPException(status_code=404, detail="todo not found")
    if not updated_todo.get("title", "").strip():
        raise HTTPException(status_code=400, detail="title is required and cannot be empty")
    updated_data = {
        "title": updated_todo["title"],
        "completed": updated_todo.get("completed", todo["completed"]),
        "updated_at": datetime.now(),
    }
    todo_collection.update_one({"_id": ObjectId(todo_id)}, {"$set": updated_data})
    updated_data["_id"] = todo_id
    return {"message": "todo updated", "data": updated_data}

# Delete a todo by ID
@app.delete("/api/v1/todos/{todo_id}")
def delete_todo(todo_id: str):
    try:
        result = todo_collection.delete_one({"_id": ObjectId(todo_id)})
    except:
        raise HTTPException(status_code=400, detail="invalid todo ID")
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="todo not found")
    return {"message": "todo deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
