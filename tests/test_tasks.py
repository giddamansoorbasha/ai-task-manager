async def test_tasks_require_auth(client):
    res = await client.get("/tasks/")
    assert res.status_code == 401


async def test_create_task_defaults(client, login_as):
    headers = await login_as()
    res = await client.post("/tasks/", json={"title": "T", "description": "D"}, headers=headers)
    assert res.status_code == 201
    assert res.json()["status"] == "todo"
    assert res.json()["due_date"] is None


async def test_create_task_with_due_date(client, login_as):
    headers = await login_as()
    res = await client.post(
        "/tasks/",
        json={"title": "T", "description": "D", "due_date": "2026-10-10T18:00:00+05:30"},
        headers=headers,
    )
    assert res.status_code == 201
    assert res.json()["due_date"] is not None


async def test_naive_due_date_rejected(client, login_as):
    headers = await login_as()
    res = await client.post(
        "/tasks/",
        json={"title": "T", "description": "D", "due_date": "2026-10-10T18:00:00"},
        headers=headers,
    )
    assert res.status_code == 422


async def test_update_status_and_filter(client, login_as):
    headers = await login_as()
    task = (await client.post("/tasks/", json={"title": "T", "description": "D"}, headers=headers)).json()
    res = await client.patch(f"/tasks/{task['task_id']}/status", json={"status": "done"}, headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "done"

    done = await client.get("/tasks/?status=done", headers=headers)
    todo = await client.get("/tasks/?status=todo", headers=headers)
    assert len(done.json()) == 1
    assert len(todo.json()) == 0


async def test_cannot_access_other_users_task(client, login_as):
    headers_a = await login_as("a@test.com")
    headers_b = await login_as("b@test.com")
    task = (await client.post("/tasks/", json={"title": "T", "description": "D"}, headers=headers_a)).json()

    assert (await client.get(f"/tasks/{task['task_id']}", headers=headers_b)).status_code == 404
    assert (await client.delete(f"/tasks/{task['task_id']}", headers=headers_b)).status_code == 404

async def test_pagination(client, login_as):
    headers = await login_as()
    for i in range(3):
        await client.post("/tasks/", json={"title": f"T{i}", "description": "D"}, headers=headers)

    page1 = await client.get("/tasks/?limit=2&offset=0", headers=headers)
    page2 = await client.get("/tasks/?limit=2&offset=2", headers=headers)
    assert len(page1.json()) == 2
    assert len(page2.json()) == 1
    assert {t["task_id"] for t in page1.json()}.isdisjoint({t["task_id"] for t in page2.json()})

    assert (await client.get("/tasks/?limit=0", headers=headers)).status_code == 422
    assert (await client.get("/tasks/?limit=101", headers=headers)).status_code == 422

async def test_delete_task(client, login_as):
    headers = await login_as()
    task = (await client.post("/tasks/", json={"title": "T", "description": "D"}, headers=headers)).json()
    assert (await client.delete(f"/tasks/{task['task_id']}", headers=headers)).status_code == 204
    assert (await client.get(f"/tasks/{task['task_id']}", headers=headers)).status_code == 404