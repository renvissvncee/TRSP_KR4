from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI()

users_db: Dict[int, dict] = {}
current_id = 1

class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None

@app.post("/users/", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate):
    global current_id  # ← ВАЖНО: добавляем global!
    user_dict = user.model_dump()  # Заменили dict() на model_dump()
    user_dict["id"] = current_id
    users_db[current_id] = user_dict
    current_id += 1
    return user_dict

@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    del users_db[user_id]
    return None

@app.get("/users/")
def get_all_users():
    return list(users_db.values())