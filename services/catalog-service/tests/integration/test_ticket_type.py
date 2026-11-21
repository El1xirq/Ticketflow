from httpx import AsyncClient
from sqlalchemy import select

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.db import TicketTypeORM

async def test_create_ticket_type(
        client: AsyncClient,
        body_ticket_type,
        event_not_published,
        organizer_headers,
        session,
):
    """POST /v1/events/{event_id}/ticket-types create ticket, status code 201"""
    response = await client.post(
        f'/v1/events/{event_not_published}/ticket-types',
        json=body_ticket_type,
        headers=organizer_headers,
    )
    assert response.status_code == 201
    body = response.json()

    ticket = (await session.execute(
        select(TicketTypeORM).where(TicketTypeORM.id == body['id'])
    )).scalar_one_or_none()
    assert ticket is not None
    assert str(ticket.event_id) == event_not_published
    assert ticket.name == body_ticket_type['name']


async def test_create_ticket_type_customer(
        client: AsyncClient,
        body_ticket_type,
        event_not_published,
        customer_headers,
):
    """POST /v1/events/{event_id}/ticket-types create ticket customer role, exception 403"""
    response = await client.post(
        f'/v1/events/{event_not_published}/ticket-types',
        json=body_ticket_type,
        headers=customer_headers,
    )
    assert response.status_code == 403


async def test_create_ticket_type_empty_title(
        client: AsyncClient,
        event_not_published,
        organizer_headers,
):
    """POST /v1/events/{event_id}/ticket-types create ticket empty title, exception 422"""
    start = datetime.now(timezone.utc) + timedelta(days=1)
    end = datetime.now(timezone.utc) + timedelta(days=3)

    
    response = await client.post(
        f'/v1/events/{event_not_published}/ticket-types',
        json={
            "name": "",
            "description": "новое описание",
            "price_minor": 8999,
            "currency": "RUB",
            "total_quantity": 30,
            "sales_start_at": str(start),
            "sales_end_at": str(end),
            "is_active": True,
            },
        headers=organizer_headers,
        )
    assert response.status_code == 422


async def test_create_ticket_type_past_start_at(
        client: AsyncClient,
        event_not_published,
        organizer_headers,
):
    """POST /v1/events/{event_id}/ticket-types create ticket invalid sales_start_at, exception 422"""
    start = datetime.now(timezone.utc) - timedelta(days=3)
    end = datetime.now(timezone.utc) + timedelta(days=3)

    response = await client.post(
        f'/v1/events/{event_not_published}/ticket-types',
        json={
            "name": "Новый билет",
            "description": "новое описание",
            "price_minor": 8999,
            "currency": "RUB",
            "total_quantity": 30,
            "sales_start_at": str(start),
            "sales_end_at": str(end),
            "is_active": True,
            },
        headers=organizer_headers,
        )
    assert response.status_code == 422


async def test_create_ticket_type_without_token(
        client: AsyncClient,
        event_not_published,
        body_ticket_type,
):
    """POST /v1/events/{event_id}/ticket-types create ticket without token, exception 401"""
    response = await client.post(
        f'/v1/events/{event_not_published}/ticket-types',
        json=body_ticket_type,
    )
    assert response.status_code == 401


async def test_get_event_tickets(
        client: AsyncClient,
        event_ticket,
):
    """GET /v1/events/{event_id}/ticket-types get event tickets, status code 200"""
    response = await client.get(
        f'/v1/events/{event_ticket[0]}/ticket-types',
    )
    assert response.status_code == 200
    body = response.json()
    assert body[0]['event_id'] == event_ticket[0]


async def test_patch_ticket_type(
        client: AsyncClient,
        event_ticket,
        organizer_headers,
        body_ticket_type,
):
    """PATCH /v1/events/{event_id}/ticket-types/{ticket_type_id} patch ticket, status code 200"""
    response = await client.patch(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}',
        json={
            "name": 'Обновленное имя',
            "description": None,
            "price_minor": None,
            "currency": None,
            "total_quantity": None,
            "sales_start_at": None,
            "sales_end_at": None,
            "is_active": None,
        },
        headers=organizer_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body['name'] == 'Обновленное имя'
    assert body['description'] == body_ticket_type['description']


async def test_patch_ticket_type_not_owner(
        client: AsyncClient,
        event_ticket,
        another_organizer_headers,
):
    response = await client.patch(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}',
        json={
            "name": 'Обновленное имя',
            "description": None,
            "price_minor": None,
            "currency": None,
            "total_quantity": None,
            "sales_start_at": None,
            "sales_end_at": None,
            "is_active": None,
        },
        headers=another_organizer_headers,
    )
    assert response.status_code == 403


async def test_delete_ticket_type(
        client: AsyncClient,
        event_ticket,
        organizer_headers,
        session,
):
    """DELETE /v1/events/{event_id}/ticket-types/{ticket_type_id}/delete delete ticket organizer, status code 204"""
    response = await client.delete(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}/delete',
        headers=organizer_headers,
    )
    assert response.status_code == 204

    ticket = (await session.execute(
        select(TicketTypeORM).where(TicketTypeORM.id == event_ticket[0])
    )).scalar_one_or_none()
    assert ticket is None


async def test_delete_ticket_type_not_owner(
        client: AsyncClient,
        event_ticket,
        another_organizer_headers,
):
    """DELETE /v1/events/{event_id}/ticket-types/{ticket_type_id}/delete delete ticket not owner, exception 403"""
    response = await client.delete(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}/delete',
        headers=another_organizer_headers,
    )
    assert response.status_code == 403


async def test_delete_ticket_type_admin(
        client: AsyncClient,
        event_ticket,
        admin_headers,
        session,
):
    """DELETE /v1/events/{event_id}/ticket-types/{ticket_type_id}/delete delete ticket admin, status code 204"""
    response = await client.delete(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}/delete',
        headers=admin_headers,
    )
    assert response.status_code == 204

    ticket = (await session.execute(
        select(TicketTypeORM).where(TicketTypeORM.id == event_ticket[0])
    )).scalar_one_or_none()
    assert ticket is None


async def test_get_ticket_by_id_success(
        client: AsyncClient,
        event_ticket,
        organizer_headers,
):
    """GET /v1/events/{event_id}/ticket-types/{ticket_type_id} get ticket by id organizer, status code 200"""
    response = await client.get(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}',
        headers=organizer_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body['id'] == event_ticket[1]
    assert body['event_id'] == event_ticket[0]


async def test_get_ticket_by_id_not_owner(
        client: AsyncClient,
        event_ticket,
        another_organizer_headers,
):
    """GET /v1/events/{event_id}/ticket-types/{ticket_type_id} get ticket by id not owner, status code 404"""
    response = await client.get(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}',
        headers=another_organizer_headers,
    )
    assert response.status_code == 404


async def test_get_ticket_by_id_admin(
        client: AsyncClient,
        event_ticket,
        admin_headers,
):
    """GET /v1/events/{event_id}/ticket-types/{ticket_type_id} get ticket by id admin, status code 200"""
    response = await client.get(
        f'/v1/events/{event_ticket[0]}/ticket-types/{event_ticket[1]}',
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body['id'] == event_ticket[1]
    assert body['event_id'] == event_ticket[0]