async def test_create_pin_requires_auth(client):
    res = await client.post("/create/pins/", json={"title": "Test", "image_url": "https://...", "board_id": 1})
    assert res.status_code in [401, 403]

async def test_create_pin_success(client, auth_headers):
    board_res = await client.post("/create/board", json={"name": "Test Board"}, headers=auth_headers)
    assert board_res.status_code == 200
    board_id = board_res.json()["id"]

    pin_res = await client.post("/create/pins/", json={
        "title": "My First Pin",
        "description": "Test description",
        "image_url": "https://via.placeholder.com/400x600",
        "board_id": board_id
    }, headers=auth_headers)

    assert pin_res.status_code == 200
    data = pin_res.json()
    assert data["title"] == "My First Pin"
    assert "id" in data
    assert "author" in data


async def test_like_pin(client, auth_headers):
    board_res = await client.post("/create/board", json={"name": "Like Board"}, headers=auth_headers)
    board_id = board_res.json()["id"]
    pin_res = await client.post("/create/pins/", json={
        "title": "Like Me", "image_url": "https://...", "board_id": board_id
    }, headers=auth_headers)
    pin_id = pin_res.json()["id"]

    like_res = await client.post(f"/pins/{pin_id}/like", headers=auth_headers)
    assert like_res.status_code == 200
    assert like_res.json()["is_liked"] is True
    assert like_res.json()["likes_count"] == 1

    unlike_res = await client.post(f"/pins/{pin_id}/like", headers=auth_headers)
    assert unlike_res.json()["is_liked"] is False
    assert unlike_res.json()["likes_count"] == 0