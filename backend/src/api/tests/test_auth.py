async def test_register_success(client):
    res = await client.post("/register", json={
        "email": "newuser@example.com",
        "username": "newuser",
        "password": "securepass123"
    })
    assert res.status_code == 201
    assert "message" in res.json()

async def test_register_duplicate(client):
    await client.post("/register", json={"email": "dup@test.com", "username": "dup", "password": "pass123"})
    res = await client.post("/register", json={"email": "dup2@test.com", "username": "dup", "password": "pass123"})
    assert res.status_code == 400

async def test_login_success(client, auth_headers):
    res = await client.post("/token", data={
        "username": "testuser",
        "password": "password123"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

async def test_login_invalid_password(client):
    await client.post("/register", json={"email": "fail@test.com", "username": "failuser", "password": "pass123"})
    res = await client.post("/token", data={
        "username": "failuser",
        "password": "wrongpassword"
    }, headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert res.status_code == 401