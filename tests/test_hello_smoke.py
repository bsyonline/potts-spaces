def test_hello_endpoint_returns_200(client):
    response = client.get("/hello")
    assert response.status_code == 200


def test_hello_endpoint_returns_message(client):
    response = client.get("/hello")
    assert "message" in response.json()