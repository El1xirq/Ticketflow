from httpx import AsyncClient
from sqlalchemy import select

from datetime import datetime, timedelta, timezone

from app.db import EventORM

async def test_create_event_access(
        client: AsyncClient,
        session,
        organizer_headers,
        body_event,
):
    """POST /v1/events create event organizer role, status code 201"""
    response = await client.post(
        '/v1/events',
        json=body_event,
        headers=organizer_headers
    )

    assert response.status_code == 201
    body = response.json()

    event = (
        await session.execute(
            select(EventORM).where(EventORM.id == body['id'])
        )
    ).scalar_one_or_none()

    assert event is not None
    assert event.title == body['title']
    assert str(event.id) == body['id']


async def test_create_event_admin(
        client: AsyncClient,
        body_event,
        admin_headers,
        session,
):
    """POST /v1/events create event admin role, status code 201"""
    response = await client.post(
        '/v1/events',
        json=body_event,
        headers=admin_headers
    )

    assert response.status_code == 201
    body = response.json()

    event = (
        await session.execute(
            select(EventORM).where(EventORM.id == body['id'])
        )
    ).scalar_one_or_none()

    assert event is not None
    assert event.title == body['title']
    assert str(event.id) == body['id']


async def test_create_event_customer_forbidden(
        client: AsyncClient,
        customer_headers,
        body_event,
):
    """POST /v1/events create event customer role, exception 403"""
    response = await client.post(
        '/v1/events',
        json=body_event,
        headers=customer_headers
    )

    assert response.status_code == 403
    body = response.json()
    assert body['error_code'] == 'FORBIDDEN'


async def test_create_event_without_token(
        client: AsyncClient,
        body_event,
):
    """POST /v1/events create event without token, exception 401"""
    response = await client.post(
        'v1/events',
        json=body_event,
    )

    assert response.status_code == 401
    body = response.json()
    assert body['error_code'] == 'UNAUTHORIZED'


async def test_create_event_empty_title(
        client: AsyncClient,
        organizer_headers,
):
    """POST /v1/events create event empty field(title), exception 422"""
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = datetime.now(timezone.utc) + timedelta(days=3)
    response = await client.post(
        '/v1/events',
        json={
            "title": "",
            "description": "новое описание",
            "venue_name": "Зал",
            "city": "Уфа",
            "address": "Главная улица, 1",
            "starts_at": str(start),
            "ends_at": str(end)            
        },
        headers=organizer_headers,
    )

    assert response.status_code == 422


async def test_create_event_past_starts_at(
        client: AsyncClient,
        organizer_headers,
):
    """POST /v1/events create event past starts_at, exception 422"""
    start = datetime.now(timezone.utc) - timedelta(days=1)
    end = datetime.now(timezone.utc) + timedelta(days=3)
    response = await client.post(
        '/v1/events',
        json={
            "title": "Мой концерт",
            "description": "новое описание",
            "venue_name": "Зал",
            "city": "Уфа",
            "address": "Главная улица, 1",
            "starts_at": str(start),
            "ends_at": str(end)            
        },
        headers=organizer_headers,
    )

    assert response.status_code == 422


async def test_create_event_past_ends_at(
        client: AsyncClient,
        organizer_headers,
):
    """POST /v1/events create event past starts_at, exception 422"""
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = datetime.now(timezone.utc) - timedelta(days=3)
    response = await client.post(
        '/v1/events',
        json={
            "title": "Мой концерт",
            "description": "новое описание",
            "venue_name": "Зал",
            "city": "Уфа",
            "address": "Главная улица, 1",
            "starts_at": str(start),
            "ends_at": str(end)            
        },
        headers=organizer_headers,
    )

    assert response.status_code == 422


async def test_get_event_id_access(
        client: AsyncClient,
        event_not_published,
        organizer_headers,
):
    """GET /v1/events/{event_id} get event by id, organizer, status code 200"""
    response = await client.get(
        f'/v1/events/{event_not_published}',
        headers=organizer_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body['id'] == event_not_published


async def test_get_list_events(
        client: AsyncClient,
        event_published,
):
    """GET /v1/events get list events, status code 200"""
    response = await client.get(
        '/v1/events',
    )
    assert response.status_code == 200
    body = response.json()
    assert body[0]['id'] == event_published