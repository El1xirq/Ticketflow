import jwt
import pytest
import pytest_asyncio
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.core.config import settings


@pytest.fixture(scope="session")
def test_jwt_keys(tmp_path_factory):
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    public_key_path = tmp_path_factory.mktemp("jwt-keys") / "public.pem"
    public_key_path.write_bytes(public_pem)

    return {
        "private_key": private_pem,
        "public_key": public_pem.decode("utf-8"),
    }


@pytest.fixture(autouse=True)
def configure_test_public_key(test_jwt_keys, monkeypatch):
    monkeypatch.setattr(
        settings,
        "jwt_public_key",
        test_jwt_keys["public_key"],
    )


@pytest.fixture
def unic_id():
    return uuid4()


@pytest.fixture
def make_access_token(test_jwt_keys):
    def make_token(user_id, roles):
        now = datetime.now(timezone.utc)

        return jwt.encode(
            {
                "sub": str(user_id),
                "roles": roles,
                "type": "access",
                "exp": now + timedelta(minutes=5),
            },
            test_jwt_keys["private_key"],
            algorithm="RS256",
        )

    return make_token


@pytest.fixture
def organizer_headers(make_access_token, unic_id):
    token = make_access_token(unic_id, ["organizer"])
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def customer_headers(make_access_token, unic_id):
    token = make_access_token(unic_id, ['customer'])
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(make_access_token, unic_id):
    token = make_access_token(unic_id, ['admin'])
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def body_event():
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = datetime.now(timezone.utc) + timedelta(days=3)

    return {
        "title": "Мой концерт",
        "description": "новое описание",
        "venue_name": "Зал",
        "city": "Уфа",
        "address": "Главная улица, 1",
        "starts_at": str(start),
        "ends_at": str(end)
    }


@pytest.fixture
def body_ticket_type():
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = datetime.now(timezone.utc) + timedelta(days=3)

    return {
        "name": "Новый билет",
        "description": "новое описаие",
        "price_minor": 8999,
        "currency": "RUB",
        "total_quantity": 30,
        "sales_start_at": str(start),
        "sales_end_at": str(end),
        "is_active": True,
    }


@pytest_asyncio.fixture
async def event_not_published(
    client,
    organizer_headers,
    body_event,
):
    response = await client.post(
        '/v1/events',
        json=body_event,
        headers=organizer_headers,
    )
    assert response.status_code == 201
    return response.json()['id']


@pytest_asyncio.fixture
async def event_ticket(
    client,
    organizer_headers,
    body_ticket_type,
    event_not_published,
):
    response = await client.post(
        f'/v1/events/{event_not_published}/ticket-types',
        json=body_ticket_type,
        headers=organizer_headers,
    )
    assert response.status_code == 201
    body = response.json()

    return (body['id'], body['event_id'])


@pytest_asyncio.fixture
async def event_published(
    client,
    organizer_headers,
    event_ticket,
):
    response = await client.post(
        f'/v1/events/{event_ticket[1]}/publish',
        headers=organizer_headers
    )
    assert response.status_code == 200
    return response.json()['id']