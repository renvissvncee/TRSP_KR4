import pytest

@pytest.mark.parametrize("name,email,age,expected_status", [
    ("Alice", "alice@test.com", 30, 201),   
    ("Bob", "bob@test.com", None, 201),     
    ("", "empty@test.com", 20, 201),       
    ("Valid", "not_an_email", 25, 201),     
])
def test_create_user_various_cases(client, name, email, age, expected_status):
    user_data = {"name": name, "email": email}
    if age is not None:
        user_data["age"] = age
    
    response = client.post("/users/", json=user_data)
    assert response.status_code == expected_status

def test_create_user_success(client):
    response = client.post("/users/", json={
        "name": "Alice",
        "email": "alice@example.com",
        "age": 25
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"
    assert data["age"] == 25
    assert "id" in data
    assert isinstance(data["id"], int)



def test_create_user_without_age(client):
    user_data = {
        "name": "Ilgiz",
        "email": "ilgiz@mail.ru"
    }
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Ilgiz"
    assert data["age"] is None  



def test_create_user_invalid_email(client):
    user_data = {
        "name": "German"
        # email отсутствует - обязательное поле!
    }
    
    response = client.post("/users/", json=user_data)
    
    assert response.status_code == 422



def test_get_user_success(client):
    create_response = client.post("/users/", json={
        "name": "Nikita",
        "email": "nikita@mail.ru"
    })
    user_id = create_response.json()["id"]
    
    # Получаем пользователя
    get_response = client.get(f"/users/{user_id}")
    
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["name"] == "Nikita"
    assert data["email"] == "nikita@mail.ru"



def test_get_user_not_found(client):
    response = client.get("/users/999")
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "User not found"



def test_delete_user_success(client):
    # Создаём
    create_response = client.post("/users/", json={
        "name": "Eve",
        "email": "eve@example.com"
    })
    user_id = create_response.json()["id"]
    
    # Удаляем
    delete_response = client.delete(f"/users/{user_id}")
    
    assert delete_response.status_code == 204
    assert delete_response.text == ""
    
    get_response = client.get(f"/users/{user_id}")
    assert get_response.status_code == 404



def test_delete_user_not_found(client):
    response = client.delete("/users/999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"



def test_get_all_users(client):
    # Создаём двух пользователей
    client.post("/users/", json={"name": "User1", "email": "user1@example.com"})
    client.post("/users/", json={"name": "User2", "email": "user2@example.com"})
    
    # Получаем всех
    response = client.get("/users/")
    
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    
    names = [user["name"] for user in users]
    assert "User1" in names
    assert "User2" in names