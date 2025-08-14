from fastapi.testclient import TestClient


def test_create_and_read_country(client: TestClient):
    response = client.post(
        "/api/v1/country/",
        json={
            "name": "Poland",
            "alpha_2_code": "PL",
            "latitude": 51.919438,
            "longitude": 19.145136,
        },
    )
    data = response.json()

    assert response.status_code == 201
    assert data["name"] == "Poland"
    assert data["alpha_2_code"] == "PL"

    country_code = data["alpha_2_code"]
    response = client.get(f"/api/v1/country/{country_code}")

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Poland"
    assert data["alpha_2_code"] == "PL"
