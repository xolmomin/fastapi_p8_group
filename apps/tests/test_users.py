def test_create_user(client):
    data = {
        'name': 'testuser',
        'email': 'testuser@test.com',
        'password': 'testing'
    }
    response = client.post("/add-user", data=data)
    response_data = response.json()
    assert response.status_code == 200
    assert response_data["email"] == data['email']
    assert not response_data["is_active"]
