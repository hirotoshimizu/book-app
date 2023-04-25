def test_graphs(client):
    response = client.get("/graphs/")
    assert response.status_code == 200
