from httpx import AsyncClient
from sqlalchemy import select

from datetime import datetime, timedelta, timezone

from app.db import EventORM
from app.core.enums import EventStatus

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


async def test_get_foreign_event_id(
        client: AsyncClient,
        event_not_published,
        another_organizer_headers,
):
    """GET /v1/events/{event_id} get foreign event by id, exception 404"""
    response = await client.get(
        f'/v1/events/{event_not_published}',
        headers=another_organizer_headers,
        )
    assert response.status_code == 404


async def test_patch_event_success(
        client: AsyncClient,
        event_not_published,
        organizer_headers,
        session,
        body_event,
):
    """PATCH /v1/events/{event_id} update event, status code 200"""
    response = await client.patch(
        f'/v1/events/{event_not_published}',
        json={
            "title": "Обновленное имя",
            "description": None,
            "venue_name": None,
            "city": None,
            "address": None,
            "starts_at": None,
            "ends_at": None,
            }    
        ,
        headers=organizer_headers,
        )
    assert response.status_code == 200
    body = response.json()

    event = (await session.execute(
        select(EventORM).where(EventORM.id == body['id'])
    )).scalar_one_or_none()
    assert event is not None
    assert event.title == body['title']
    assert event.description == body_event['description']


async def test_patch_event_not_owner(
        client: AsyncClient,
        event_not_published,
        another_organizer_headers,
):
    """PATCH /v1/events/{event_id} update event not owner, exception 403"""
    response = await client.patch(
        f'/v1/events/{event_not_published}',
        json={
            "title": "Обновленное имя",
            "description": None,
            "venue_name": None,
            "city": None,
            "address": None,
            "starts_at": None,
            "ends_at": None,
            },
        headers=another_organizer_headers,
        )
    assert response.status_code == 403


async def test_publish_event_not_active_tickets(
        client: AsyncClient,
        event_not_published,
        organizer_headers,
):
    """POST /v1/events/{event_id}/publish publish event not active tickets, exception 409"""
    response = await client.post(
        f'/v1/events/{event_not_published}/publish',
        headers=organizer_headers,
    )
    assert response.status_code == 400


async def test_publish_event_success(
        client: AsyncClient,
        organizer_headers,
        event_ticket,
        session,
):
    """POST /v1/events/{event_id}/publish success publish organizer, status code 200"""
    response = await client.post(
        f'/v1/events/{event_ticket[0]}/publish',
        headers=organizer_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body['status'] == EventStatus.PUBLISHED.value

    event = (await session.execute(
        select(EventORM).where(EventORM.id == body['id'])
    )).scalar_one_or_none()
    assert event is not None
    assert event.status == EventStatus.PUBLISHED.value
    assert event.published_at is not None


async def test_publish_event_admin(
        client: AsyncClient,
        admin_headers,
        event_ticket,
):
    """POST /v1/events/{event_id}/publish success publish admin, status code 200"""
    response = await client.post(
        f'/v1/events/{event_ticket[0]}/publish',
        headers=admin_headers,
    )
    assert response.status_code == 200


async def test_publish_foreign_event(
        client: AsyncClient,
        another_organizer_headers,
        event_ticket,
):
    """POST /v1/events/{event_id}/publish publish event another organizer, exception 403"""
    response = await client.post(
        f'/v1/events/{event_ticket[0]}/publish',
        headers=another_organizer_headers,
    )
    assert response.status_code == 403

async def test_cancel_event_success(
        client: AsyncClient,
        event_not_published,
        organizer_headers, 
        session,
):
    """POST /v1/events/{event_id}/cancel cancel event organizer, status code 204"""
    response = await client.post(
        f'/v1/events/{event_not_published}/cancel',
        headers=organizer_headers,
    )
    assert response.status_code == 204

    event = (await session.execute(
        select(EventORM).where(EventORM.id == event_not_published)
    )).scalar_one_or_none()
    assert event is not None
    assert event.status == EventStatus.CANCELLED.value


async def test_cancel_foreign_event(
        client: AsyncClient,
        event_not_published,
        another_organizer_headers,
):
    """POST /v1/events/{event_id}/cancel cancel event another organizer, exception 403"""
    response = await client.post(
        f'/v1/events/{event_not_published}/cancel',
        headers=another_organizer_headers,
    )
    assert response.status_code == 403


async def test_cancel_event_admin(
        client: AsyncClient,
        event_not_published,
        admin_headers,
):
    """POST /v1/events/{event_id}/cancel cancel event admin, status code 204"""
    response = await client.post(
        f'/v1/events/{event_not_published}/cancel',
        headers=admin_headers,
    )
    assert response.status_code == 204


async def test_delete_event_organizer(
        client: AsyncClient,
        event_not_published,
        organizer_headers,
        session,
):
    """DELETE /v1/events/{event_id}/delete delete event organizer, status code 204"""
    response = await client.delete(
        f'/v1/events/{event_not_published}/delete',
        headers=organizer_headers,
    )
    assert response.status_code == 204

    event = (await session.execute(
        select(EventORM).where(EventORM.id == event_not_published)
    )).scalar_one_or_none()
    assert event is None


async def test_delete_event_not_owner(
        client: AsyncClient,
        event_not_published,
        another_organizer_headers,
):
    """DELETE /v1/events/{event_id}/delete delete event not owner, exception 403"""
    response = await client.delete(
        f'/v1/events/{event_not_published}/delete',
        headers=another_organizer_headers,
    )
    assert response.status_code == 403


async def test_delete_event_admin(
        client: AsyncClient,
        event_not_published,
        admin_headers,
        session,
):
    """DELETE /v1/events/{event_id}/delete delete event admin, status code 204"""
    response = await client.delete(
        f'/v1/events/{event_not_published}/delete',
        headers=admin_headers,
    )
    assert response.status_code == 204

    event = (await session.execute(
        select(EventORM).where(EventORM.id == event_not_published)
    )).scalar_one_or_none()
    assert event is None