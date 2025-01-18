import sqlite3
from fastapi import FastAPI, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

app = FastAPI()

# Database setup
DB_FILE = "sqlite_3_todos.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)
        conn.commit()

init_db()

def query_db(query: str, args: tuple = (), one: bool = False):
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(query, args)
        rows = cursor.fetchall()
        conn.commit()
        return (rows[0] if rows else None) if one else rows

# Pydantic models for validation
class TodoCreate(BaseModel):
    title: str
    completed: Optional[bool] = False

class TodoUpdate(BaseModel):
    title: Optional[str]
    completed: Optional[bool]

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: str
    updated_at: str

# Routes

@app.get("/api/v1/todos", response_model=List[TodoResponse])
def get_todos(
    title: Optional[str] = Query(None), 
    completed: Optional[bool] = Query(None)
):
    query = "SELECT * FROM todos WHERE 1=1"
    params = []

    if title:
        query += " AND title LIKE ?"
        params.append(f"%{title}%")
    if completed is not None:
        query += " AND completed = ?"
        params.append(1 if completed else 0)

    todos = query_db(query, tuple(params))
    return [dict(todo) for todo in todos]

@app.post("/api/v1/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    created_at = updated_at = datetime.utcnow().isoformat()
    query = """
        INSERT INTO todos (title, completed, created_at, updated_at)
        VALUES (?, ?, ?, ?)
    """
    params = (todo.title, todo.completed, created_at, updated_at)

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        todo_id = cursor.lastrowid

    new_todo = {
        "id": todo_id,
        "title": todo.title,
        "completed": todo.completed,
        "created_at": created_at,
        "updated_at": updated_at
    }
    return new_todo

@app.get("/api/v1/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    todo = query_db("SELECT * FROM todos WHERE id = ?", (todo_id,), one=True)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return dict(todo)

@app.put("/api/v1/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, updated_todo: TodoUpdate):
    todo = query_db("SELECT * FROM todos WHERE id = ?", (todo_id,), one=True)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    fields = []
    params = []

    if updated_todo.title is not None:
        fields.append("title = ?")
        params.append(updated_todo.title)
    if updated_todo.completed is not None:
        fields.append("completed = ?")
        params.append(1 if updated_todo.completed else 0)

    params.append(datetime.utcnow().isoformat())  # updated_at
    params.append(todo_id)

    query = f"UPDATE todos SET {', '.join(fields)}, updated_at = ? WHERE id = ?"
    query_db(query, tuple(params))

    updated_todo = query_db("SELECT * FROM todos WHERE id = ?", (todo_id,), one=True)
    return dict(updated_todo)

@app.delete("/api/v1/todos/{todo_id}", response_model=dict)
def delete_todo(todo_id: int):
    todo = query_db("SELECT * FROM todos WHERE id = ?", (todo_id,), one=True)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    query_db("DELETE FROM todos WHERE id = ?", (todo_id,))
    return {"message": "Todo deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
