from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorModel(BaseModel):
    error: str
    code: int
    
app = FastAPI()

class ItemNotFoundException(HTTPException):
    def __init__(self, item_name: str):
        super().__init__(
            status_code=404,
            detail=f"Товар '{item_name}' отсутствует в базе"
        )

class AccessDeniedException(HTTPException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=403,
            detail=f"Доступ запрещен: {reason}"
        )

# Обработчик для первого исключения
@app.exception_handler(ItemNotFoundException)
async def item_not_found_handler(request: Request, exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content=ErrorModel(error=exc.detail, code=404).model_dump()
    )

# Обработчик для второго исключения
@app.exception_handler(AccessDeniedException)
async def access_denied_handler(request: Request, exc: AccessDeniedException):
    return JSONResponse(
        status_code=403,
        content=ErrorModel(error=exc.detail, code=403).model_dump()
    )

# Тестовые эндпоинты
@app.get("/item/{item_id}")
async def get_item(item_id: int):
    if item_id == 999:
        raise ItemNotFoundException("Ноутбук")
    return {"item_id": item_id, "name": "Телефон"}

@app.get("/admin")
async def admin_panel(role: str = "user"):
    if role != "admin":
        raise AccessDeniedException("Требуются права администратора")
    return {"message": "Добро пожаловать в админку!"}