import pytest
from my_app.main import db

@pytest.mark.asyncio
async def test_create_user_success(client, fake_user):
    """
    Тест 1: Успешное создание пользователя (201)
    Проверяем структуру ответа и сохранение в БД
    """
    user_data = fake_user(age=25)
    
    response = await client.post("/users", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    
    # Проверяем структуру ответа
    assert "id" in data
    assert data["username"] == user_data["username"]
    assert data["age"] == user_data["age"]
    assert isinstance(data["id"], int)
    
    # Проверяем, что пользователь действительно сохранен
    user_id = data["id"]
    assert user_id in db
    assert db[user_id]["username"] == user_data["username"]

@pytest.mark.asyncio
async def test_create_user_different_ages(client, fake_user):
    """
    Тест 2: Создание пользователей с разным возрастом (граничные значения)
    """
    test_cases = [1, 18, 65, 100, 150]  # Разные возраста
    
    for age in test_cases:
        user_data = fake_user(age=age)
        response = await client.post("/users", json=user_data)
        assert response.status_code == 201
        data = response.json()
        assert data["age"] == age

@pytest.mark.asyncio
async def test_create_user_missing_field(client):
    """
    Тест 3: Ошибка валидации - отсутствует обязательное поле
    """
    # Отправляем без поля age
    response = await client.post("/users", json={
        "username": "testuser"
    })
    assert response.status_code == 422  # Ошибка валидации

@pytest.mark.asyncio
async def test_get_user_success(client, fake_user):
    """
    Тест 4: Успешное получение существующего пользователя (200)
    """
    # Сначала создаем пользователя
    create_response = await client.post("/users", json=fake_user(age=30))
    user_id = create_response.json()["id"]
    
    # Получаем его
    get_response = await client.get(f"/users/{user_id}")
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["id"] == user_id
    assert "username" in data
    assert "age" in data

@pytest.mark.asyncio
async def test_get_user_not_found(client):
    """
    Тест 5: Попытка получить несуществующего пользователя (404)
    """
    response = await client.get("/users/99999")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"

@pytest.mark.asyncio
async def test_delete_user_success(client, fake_user):
    """
    Тест 6: Успешное удаление пользователя (204)
    """
    # Создаем пользователя
    create_response = await client.post("/users", json=fake_user(age=20))
    user_id = create_response.json()["id"]
    
    # Удаляем его
    delete_response = await client.delete(f"/users/{user_id}")
    
    assert delete_response.status_code == 204
    assert delete_response.text == ""  # Нет тела ответа при 204
    
    # Проверяем, что пользователь действительно удален
    get_response = await client.get(f"/users/{user_id}")
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_user_not_found(client):
    """
    Тест 7: Повторное удаление того же пользователя (404)
    А также удаление несуществующего
    """
    # Пытаемся удалить несуществующего
    response = await client.delete("/users/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"

@pytest.mark.asyncio
async def test_delete_twice_same_user(client, fake_user):
    """
    Тест 8: Удаление дважды одного пользователя
    Первый раз - 204, второй - 404
    """
    # Создаем
    create_response = await client.post("/users", json=fake_user(age=25))
    user_id = create_response.json()["id"]
    
    # Удаляем первый раз
    response1 = await client.delete(f"/users/{user_id}")
    assert response1.status_code == 204
    
    # Удаляем второй раз (того же пользователя)
    response2 = await client.delete(f"/users/{user_id}")
    assert response2.status_code == 404

@pytest.mark.asyncio
async def test_multiple_users_isolation(client, fake_user):
    """
    Тест 9: Проверка изоляции между разными пользователями
    """
    # Создаем несколько пользователей
    users = []
    for i in range(3):
        response = await client.post("/users", json=fake_user(age=20 + i))
        users.append(response.json())
    
    # Проверяем, что у всех разные ID
    ids = [user["id"] for user in users]
    assert len(set(ids)) == 3  # Все ID уникальны
    
    # Проверяем, что каждый доступен
    for user in users:
        get_response = await client.get(f"/users/{user['id']}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == user["id"]

@pytest.mark.asyncio
async def test_create_user_with_max_age(client, fake_user):
    """
    Тест 10: Граничное значение - максимальный возраст
    """
    user_data = fake_user(age=999)
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["age"] == 999

@pytest.mark.asyncio
async def test_create_user_with_min_age(client, fake_user):
    """
    Тест 11: Граничное значение - минимальный возраст
    """
    user_data = fake_user(age=0)
    response = await client.post("/users", json=user_data)
    assert response.status_code == 201
    assert response.json()["age"] == 0