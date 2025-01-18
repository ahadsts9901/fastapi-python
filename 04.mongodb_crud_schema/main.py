import os
from fastapi import FastAPI, HTTPException, Query, Body
from typing import Optional, List
from mongoengine import connect, Document, StringField, BooleanField, DateTimeField
from pydantic import BaseModel
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# MongoDB connection setup using MongoEngine
mongo_url = os.getenv("MONGO_URI")
if not mongo_url:
    raise ValueError("MONGO_URI environment variable not set")

connect("todo_db_python_schema_fastapi", host=mongo_url)

# Define the Todo schema using MongoEngine
class Todo(Document):
    title = StringField(required=True)
    completed = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": str(self.id),
            "title": self.title,
            "completed": self.completed,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

# Pydantic models for request validation
class TodoCreate(BaseModel):
    title: str
    completed: Optional[bool] = False

class TodoUpdate(BaseModel):
    title: Optional[str]
    completed: Optional[bool]

# Routes

@app.get("/api/v1/todos", response_model=List[dict])
def get_todos(title: Optional[str] = Query(None), completed: Optional[bool] = Query(None)):
    filters = {}
    if title:
        filters["title__icontains"] = title  # Case insensitive search
    if completed is not None:
        filters["completed"] = completed

    todos = Todo.objects(**filters)
    return {
        "message": "todos fetched",
        "data": [todo.to_dict() for todo in todos]
    }

@app.post("/api/v1/todos", response_model=dict, status_code=201)
def create_todo(todo: TodoCreate):
    new_todo = Todo(
        title=todo.title,
        completed=todo.completed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    new_todo.save()
    return {"message": "todo created successfully", "data": new_todo.to_dict()}

@app.get("/api/v1/todos/{todo_id}", response_model=dict)
def get_todo(todo_id: str):
    try:
        todo = Todo.objects.get(id=todo_id)
        return {"message": "todo fetched successfully", "data": todo.to_dict()}
    except Todo.DoesNotExist:
        raise HTTPException(status_code=404, detail="todo not found")

@app.put("/api/v1/todos/{todo_id}", response_model=dict)
def update_todo(todo_id: str, updated_todo: TodoUpdate):
    try:
        todo = Todo.objects.get(id=todo_id)
    except Todo.DoesNotExist:
        raise HTTPException(status_code=404, detail="todo not found")

    if updated_todo.title is not None:
        todo.title = updated_todo.title
    if updated_todo.completed is not None:
        todo.completed = updated_todo.completed

    todo.updated_at = datetime.utcnow()
    todo.save()
    return {"message": "todo updated successfully", "data": todo.to_dict()}

@app.delete("/api/v1/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: str):
    try:
        todo = Todo.objects.get(id=todo_id)
        todo.delete()
        return {"message": "todo deleted successfully"}
    except Todo.DoesNotExist:
        raise HTTPException(status_code=404, detail="todo not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
