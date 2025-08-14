from fastapi.testclient import TestClient


def test_create_player_with_valid_nationality(client: TestClient):
    client.post(
        "/api/v1/country/",
        json={
            "name": "Brazil",
            "alpha_2_code": "BR",
            "latitude": -14.235004,
            "longitude": -51.92528,
        },
    )

    response = client.post(
        "/api/v1/player/",
        json={
            "first_name": "Giba",
            "last_name": "Godoy",
            "date_of_birth": "1976-12-23",
            "nationality_code": "BR",
            "height_cm": 192,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "Giba"
    assert data["last_name"] == "Godoy"
    assert data["date_of_birth"] == "1976-12-23"
    assert data["nationality_code"] == "BR"
    assert data["height_cm"] == 192


def test_create_player_with_nonexistent_nationality_fails(client: TestClient):
    response = client.post(
        "/api/v1/player/",
        json={
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "2000-01-01",
            "nationality_code": "XX",  # no such country
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert "Database integrity error" in data["detail"]


def test_get_player_by_id_returns_404_for_nonexistent(client: TestClient):
    # 404 error handling
    non_existent_uuid = "a1b2c3d4-e5f6-a7b8-c9d0-e1f2a3b4c5d6"
    response = client.get(f"/api/v1/player/{non_existent_uuid}")
    assert response.status_code == 404


def test_update_player(client: TestClient):
    client.post(
        "/api/v1/country/",
        json={
            "name": "Poland",
            "alpha_2_code": "PL",
            "latitude": 51.919438,
            "longitude": 19.145136,
        },
    )

    response = client.post(
        "/api/v1/player/",
        json={
            "first_name": "Bartosz",
            "last_name": "Kurek",
            "date_of_birth": "1988-08-29",
            "nationality_code": "PL",
        },
    )

    player_id = response.json()["id"]

<<<<<<< HEAD
<<<<<<< HEAD
    response = client.patch(f"/api/v1/players/{player_id}", json={ "height_cm": 205} )
=======
    response = client.patch(f"/api/v1/players/{player_id}", json={"height_cm": 205})
>>>>>>> feature/seeding
=======
    response = client.patch(f"/api/v1/player/{player_id}", json={"height_cm": 205})
>>>>>>> feature/seeding

    assert response.status_code == 200
    data = response.json()
    assert data["height_cm"] == 205
    assert data["first_name"] == "Bartosz"
    assert data["last_name"] == "Kurek"


def test_update_player_with_nonexistent_nationality_fails(client: TestClient):
    client.post(
        "/api/v1/country/",
        json={
            "name": "Poland",
            "alpha_2_code": "PL",
            "latitude": 51.919438,
            "longitude": 19.145136,
        },
    )

    response = client.post(
        "/api/v1/player/",
        json={
            "first_name": "Bartosz",
            "last_name": "Kurek",
            "date_of_birth": "1988-08-29",
            "nationality_code": "PL",
        },
    )

    player_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/player/{player_id}", json={"nationality_code": "XX"}
    )

    assert response.status_code == 409
    data = response.json()
    assert "Database integrity error" in data["detail"]
