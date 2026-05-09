import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.appointments import (
    format_slot,
    get_available_slots,
    get_appointments_by_cpf,
    create_appointment,
    cancel_appointment,
    reschedule_appointment,
)
from app.db.models import AppointmentStatus


# --- format_slot ---

def test_format_slot_weekday():
    # 2024-01-15 is a Monday
    dt = datetime(2024, 1, 15, 8, 0)
    result = format_slot(dt)
    assert "Segunda-feira" in result
    assert "15/01" in result
    assert "08:00" in result


def test_format_slot_friday():
    dt = datetime(2024, 1, 19, 14, 30)
    result = format_slot(dt)
    assert "Sexta-feira" in result
    assert "14:30" in result


# --- get_available_slots ---

@pytest.mark.asyncio
async def test_get_available_slots_returns_list(tmp_path):
    from app.db.engine import engine
    from app.db.models import Base, Slot
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    from sqlalchemy.ext.asyncio import AsyncSession
    TestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    future_dt = datetime.now() + timedelta(days=1)
    async with TestSession() as session:
        session.add(Slot(datetime=future_dt, available=True))
        await session.commit()

    with patch("app.services.appointments.AsyncSessionLocal", TestSession):
        slots = await get_available_slots(days=7)

    assert len(slots) == 1
    slot_id, slot_dt = slots[0]
    assert slot_dt.date() == future_dt.date()


# --- create_appointment + cancel_appointment ---

@pytest.mark.asyncio
async def test_create_and_cancel_appointment():
    from app.db.engine import engine
    from app.db.models import Base, Slot
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    future_dt = datetime.now() + timedelta(days=2)
    async with TestSession() as session:
        slot = Slot(datetime=future_dt, available=True)
        session.add(slot)
        await session.commit()
        slot_id = slot.id

    with patch("app.services.appointments.AsyncSessionLocal", TestSession):
        appt = await create_appointment("Maria Silva", "12345678900", "5511999999999", "Hemograma", slot_id)
        assert appt.id is not None
        assert appt.patient_name == "Maria Silva"
        assert appt.cpf == "12345678900"
        assert appt.status == AppointmentStatus.pending

        cancelled = await cancel_appointment(appt.id)
        assert cancelled is True

        cancelled_again = await cancel_appointment(appt.id)
        assert cancelled_again is False


# --- reschedule_appointment ---

@pytest.mark.asyncio
async def test_reschedule_appointment():
    from app.db.models import Base, Slot
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    dt1 = datetime.now() + timedelta(days=1)
    dt2 = datetime.now() + timedelta(days=3)
    async with TestSession() as session:
        slot1 = Slot(datetime=dt1, available=True)
        slot2 = Slot(datetime=dt2, available=True)
        session.add_all([slot1, slot2])
        await session.commit()
        slot1_id, slot2_id = slot1.id, slot2.id

    with patch("app.services.appointments.AsyncSessionLocal", TestSession):
        appt = await create_appointment("João Costa", "98765432100", "5511888888888", "Glicemia", slot1_id)
        updated = await reschedule_appointment(appt.id, slot2_id)

    assert updated is not None
    assert updated.slot_id == slot2_id


# --- get_appointments_by_cpf ---

@pytest.mark.asyncio
async def test_get_appointments_by_cpf():
    from app.db.models import Base, Slot
    from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

    test_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    TestSession = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)

    future_dt = datetime.now() + timedelta(days=1)
    async with TestSession() as session:
        slot = Slot(datetime=future_dt, available=True)
        session.add(slot)
        await session.commit()
        slot_id = slot.id

    with patch("app.services.appointments.AsyncSessionLocal", TestSession):
        await create_appointment("Ana Lima", "111.222.333-44", "5511777777777", "TSH", slot_id)
        # CPF with formatting should still match
        rows = await get_appointments_by_cpf("111.222.333-44")

    assert len(rows) == 1
    assert rows[0].exam_type == "TSH"
