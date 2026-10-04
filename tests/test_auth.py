async def test_signup_success(client):
    res = await client.post("/auth/signup", json={"name": "A", "email": "a@test.com", "password": "Pass1234!"})
    assert res.status_code == 200
    assert res.json()["email"] == "a@test.com"
    assert "password" not in res.json()
    assert "hashed_password" not in res.json()


async def test_signup_duplicate_email(client):
    payload = {"name": "A", "email": "a@test.com", "password": "Pass1234!"}
    await client.post("/auth/signup", json=payload)
    res = await client.post("/auth/signup", json=payload)
    assert res.status_code == 400


async def test_login_success(client):
    await client.post("/auth/signup", json={"name": "A", "email": "a@test.com", "password": "Pass1234!"})
    res = await client.post("/auth/login", data={"username": "a@test.com", "password": "Pass1234!"})
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"


async def test_login_wrong_password(client):
    await client.post("/auth/signup", json={"name": "A", "email": "a@test.com", "password": "Pass1234!"})
    res = await client.post("/auth/login", data={"username": "a@test.com", "password": "wrong"})
    assert res.status_code == 401