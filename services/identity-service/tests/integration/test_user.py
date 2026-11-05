from httpx import AsyncClient

async def test_me_success(client: AsyncClient, auth_tokens):
    """GET /v1/users/me is user, return info user"""
    response = await client.get(
        "/v1/users/me", headers={"Authorization": f"Bearer {auth_tokens['access']}"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["id"]
    assert body["email"] == "test@test.com"
    assert body["role"]
    assert body["is_active"]


async def test_me_without_token(client: AsyncClient):
    """GET /v1/users/me without token in headers, exception 401"""
    response = await client.get("/v1/users/me")
    assert response.status_code == 401


async def test_me_invalid_token(client: AsyncClient):
    """GET /v1/users/me invalid token in headers, exception 401"""
    response = await client.get(
        "/v1/users/me", headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error_code"] == "UNAUTHORIZED"


async def test_me_refresh_instead_of_access(client: AsyncClient, auth_tokens):
    """GET /v1/users/me refresh_token in headers, exception 401"""
    response = await client.get(
        "/v1/users/me", headers={"Authorization": f"Bearer {auth_tokens['refresh']}"}
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error_code"] == "UNAUTHORIZED"