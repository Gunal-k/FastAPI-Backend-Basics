from fastapi import FastAPI, Depends, HTTPException
from schemas import Todo as TodoSchema,TodoCreate
from sqlalchemy.orm import Session
from database import SessionLocal, Base, engine
from models import Todo as TodoModel

Base.metadata.create_all(bind= engine) # Create tables

app = FastAPI()

#dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db # Provide the database session 
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": "FastAPI Day 1 working"}

# Create a new todo
@app.post("/todos",response_model=TodoSchema)
def create(todo: TodoCreate,db:Session=Depends(get_db)): #
    db_todo = TodoModel(**todo.dict()) # Unpack the todo data into the model
    db.add(db_todo) # Add the new todo to the session
    db.commit() # Commit the transaction
    db.refresh(db_todo) # Refresh to get the generated ID
    return db_todo

# Get all todos
@app.get("/todos",response_model=list[TodoSchema])
def read(db:Session=Depends(get_db)):
    todos = db.query(TodoModel).all() # Query all todos
    return todos

# Get a specific todo by ID
@app.get("/todos/{todo_id}",response_model=TodoSchema)
def read_todo(todo_id:int,db:Session=Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id==todo_id).first() # Query todo by ID
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

# Update a todo by ID
@app.put("/todos/{todo_id}",response_model=TodoSchema)
def update_todo(todo_id:int,updated_todo:TodoCreate,db:Session=Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id==todo_id).first() # Query todo by ID
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    for key, value in updated_todo.dict().items(): # Update fields
        setattr(todo, key, value)
    # Alternatively, you can do:
    # todo.title = updated_todo.title
    # todo.description = updated_todo.description
    # todo.completed = updated_todo.completed
    db.commit() # Commit the transaction
    db.refresh(todo) # Refresh to get the updated data
    return todo

# Delete a todo by ID
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id:int,db:Session=Depends(get_db)):
    todo = db.query(TodoModel).filter(TodoModel.id==todo_id).first() # Query todo by ID
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    db.delete(todo) # Delete the todo
    db.commit() # Commit the transaction
    return {"message": "Todo deleted successfully"}

#delete all todos
# @app.delete("/todos")
# def delete_all_todos(db:Session=Depends(get_db)):
#     deleted = db.query(TodoModel).delete() # Delete all todos
#     db.commit() # Commit the transaction
#     return {"detail": f"Deleted {deleted} todos successfully"}