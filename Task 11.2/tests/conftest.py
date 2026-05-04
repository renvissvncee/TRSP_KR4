# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from faker import Faker
from my_app.main import app, db, _id_seq
import itertools

# Глобальный экземпляр Faker
fake = Faker()

@pytest.fixture(scope="session")
def faker():
    """Фикстура для Faker на всю сессию тестов"""
    return fake

@pytest.fixture
def user_data(faker):
    """
    Фикстура для генерации данных пользователя (возвращает словарь)
    """
    def _user_data(age: int = None, username: str = None):
        return {
            "username": username or faker.user_name(),
            "age": age if age is not None else faker.random_int(min=1, max=100)
        }
    return _user_data

@pytest.fixture
def fake_user(user_data):
    """
    АЛИАС для user_data (чтобы тесты работали с именем fake_user)
    """
    return user_data

@pytest.fixture(autouse=True)
def reset_database():
    """Сбрасываем базу данных перед каждым тестом"""
    db.clear()
    # Пересоздаем счетчик ID
    import my_app.main as main_module
    main_module._id_seq = itertools.count(start=1)
    yield

@pytest.fixture
async def client():
    """Асинхронный клиент для тестирования"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client