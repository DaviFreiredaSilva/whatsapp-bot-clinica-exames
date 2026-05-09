from datetime import date, datetime, timedelta

from sqlalchemy import func, select, update

from app.db.engine import AsyncSessionLocal, engine
from app.db.models import Appointment, AppointmentStatus, Base, Slot

_WEEKDAYS_PT = [
    "Segunda-feira",
    "Terça-feira",
    "Quarta-feira",
    "Quinta-feira",
    "Sexta-feira",
    "Sábado",
    "Domingo",
]


def format_slot(dt: datetime) -> str:
    return f"{_WEEKDAYS_PT[dt.weekday()]}, {dt.strftime('%d/%m às %H:%M')}"


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_slots()


async def _seed_slots(days_ahead: int = 30) -> None:
    async with AsyncSessionLocal() as session:
        count = await session.scalar(select(func.count()).select_from(Slot))
        if count and count > 0:
            return

        today = date.today()
        slots: list[Slot] = []
        current = today
        days_added = 0

        while days_added < days_ahead:
            if current.weekday() < 5:  # Mon–Fri only
                for hour in range(7, 17):
                    for minute in (0, 30):
                        slots.append(
                            Slot(datetime=datetime(current.year, current.month, current.day, hour, minute))
                        )
                days_added += 1
            current += timedelta(days=1)

        session.add_all(slots)
        await session.commit()


async def get_available_slots(days: int = 7) -> list[tuple[int, datetime]]:
    """Returns list of (slot_id, datetime) for available slots in the next N days."""
    cutoff = datetime.now() + timedelta(days=days)
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Slot.id, Slot.datetime)
            .where(Slot.available)
            .where(Slot.datetime >= datetime.now())
            .where(Slot.datetime <= cutoff)
            .order_by(Slot.datetime)
            .limit(10)
        )
        return result.all()


async def get_appointments_by_cpf(cpf: str) -> list[tuple[int, str, datetime, str]]:
    """Returns list of (appointment_id, exam_type, slot_datetime, status) for active appointments."""
    clean_cpf = "".join(c for c in cpf if c.isdigit())
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Appointment.id, Appointment.exam_type, Slot.datetime, Appointment.status)
            .join(Slot, Appointment.slot_id == Slot.id)
            .where(Appointment.cpf == clean_cpf)
            .where(Appointment.status != AppointmentStatus.cancelled)
            .order_by(Slot.datetime)
        )
        return result.all()


async def create_appointment(
    name: str,
    cpf: str,
    phone: str,
    exam_type: str,
    slot_id: int,
) -> Appointment:
    clean_cpf = "".join(c for c in cpf if c.isdigit())
    async with AsyncSessionLocal() as session:
        await session.execute(update(Slot).where(Slot.id == slot_id).values(available=False))
        appt = Appointment(
            patient_name=name,
            cpf=clean_cpf,
            phone=phone,
            exam_type=exam_type,
            slot_id=slot_id,
        )
        session.add(appt)
        await session.commit()
        await session.refresh(appt)
        return appt


async def cancel_appointment(appointment_id: int) -> bool:
    async with AsyncSessionLocal() as session:
        appt = await session.get(Appointment, appointment_id)
        if not appt or appt.status == AppointmentStatus.cancelled:
            return False
        appt.status = AppointmentStatus.cancelled
        await session.execute(update(Slot).where(Slot.id == appt.slot_id).values(available=True))
        await session.commit()
        return True


async def reschedule_appointment(appointment_id: int, new_slot_id: int) -> Appointment | None:
    async with AsyncSessionLocal() as session:
        appt = await session.get(Appointment, appointment_id)
        if not appt or appt.status == AppointmentStatus.cancelled:
            return None
        await session.execute(update(Slot).where(Slot.id == appt.slot_id).values(available=True))
        await session.execute(update(Slot).where(Slot.id == new_slot_id).values(available=False))
        appt.slot_id = new_slot_id
        appt.status = AppointmentStatus.pending
        appt.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(appt)
        return appt
