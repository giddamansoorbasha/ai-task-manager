from app.services.ai import AIServiceError


async def test_summary_requires_auth(client):
    assert (await client.post("/ai/summary")).status_code == 401


async def test_summary_no_tasks_skips_llm(client, login_as):
    headers = await login_as()
    res = await client.post("/ai/summary", headers=headers)
    assert res.status_code == 200
    assert res.json()["task_count"] == 0


async def test_summary_with_tasks(client, login_as, monkeypatch):
    async def fake(tasks):
        return "fake summary"

    monkeypatch.setattr("app.routes.ai.summarize_tasks", fake)
    headers = await login_as()
    await client.post("/tasks/", json={"title": "T", "description": "D"}, headers=headers)
    res = await client.post("/ai/summary", headers=headers)
    assert res.json() == {"summary": "fake summary", "task_count": 1}


async def test_summary_ai_failure_returns_502(client, login_as, monkeypatch):
    async def boom(tasks):
        raise AIServiceError("down")

    monkeypatch.setattr("app.routes.ai.summarize_tasks", boom)
    headers = await login_as()
    await client.post("/tasks/", json={"title": "T", "description": "D"}, headers=headers)
    assert (await client.post("/ai/summary", headers=headers)).status_code == 502