from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, conint, constr
from typing import Optional


class User(BaseModel):
    username: str
    age: conint(gt=18)
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'

app = FastAPI()

@app.exception_handler(RequestValidationError)
def excheption_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = err["loc"][-1]  
        errors.append({"field": field, "error": err["msg"]})

    return JSONResponse(
        status_code=422,
        content={"validation_errors": errors}
    )


@app.post('/user') 
async def create_user(user: User):
    return {"message": "User created", "user": user}

@app.get('/item/{item_id}')
def get_item(item_id: int):
    if item_id == 666:
        raise HTTPException(status_code=404, detail="Item not found")


