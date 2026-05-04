# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from my_app.main import app, db, _id_seq

@pytest.fixture(autouse=True)
def reset_state():
    db.clear()
    from my_app.main import _id_seq as seq
    import my_app.main as main_module
    main_module._id_seq = __import__('itertools').count(start=1)
    yield

@pytest.fixture
async def client():
    """
    Асинхронная фикстура, создающая HTTP клиент.
    Использует ASGITransport для прямого вызова приложения.
    """
    transport = ASGITransport(app=app)  # Подключаемся к приложению напрямую
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest.fixture
def fake_user(faker):
    """
    Фикстура для генерации тестовых пользователей с помощью Faker
    """
    def _fake_user(age: int = None):
        return {
            "username": faker.user_name(),
            "age": age if age is not None else faker.random_int(min=1, max=100)
        }
    return _fake_user