# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import json
from pathlib import Path
from typing import Optional
from utils.timestmp import utcnow
import asyncio
import os


data_dir = Path("data")
tickets_path = Path("data/tickets.json")
default_data = {}
lock = asyncio.Lock()


def ensure() -> None:
    data_dir.mkdir(exist_ok=True)
    if not tickets_path.exists():
        with open(tickets_path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)
    elif os.path.getsize(tickets_path) == 0:
        with open(tickets_path, "w", encoding="utf-8") as file:
            json.dump(default_data, file, indent=4)


async def load_tickets() -> dict:
    ensure()
    async with lock:
        try:
            with open(tickets_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
                return {}
        except json.JSONDecodeError:
            with open(tickets_path, "r", encoding="utf-8") as file:
                data = file.read()
                with open(
                    Path("data/corrupted_tickets.txt"), "a", encoding="utf-8"
                ) as corrupted_file:
                    corrupted_file.write(data)

            await save_tickets({})
            return {}


async def save_tickets(data: dict):
    ensure()
    async with lock:
        with open(tickets_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)


async def get_ticket(channel_id: int) -> Optional[dict]:
    tickets = await load_tickets()
    return tickets.get(str(channel_id))


async def get_tickets_and_ticket(channel_id: int):
    tickets = await load_tickets()
    return tickets, tickets.get(str(channel_id))


async def create_ticket(channel_id: int, owner_id: int, purpose: str) -> dict:
    tickets = await load_tickets()
    if str(channel_id) in tickets:
        raise ValueError("Ticket already exists for this channel")
    ticket = {
        "channel_id": channel_id,
        "owner_id": owner_id,
        "claimer_id": None,
        "message_id": None,
        "selected_purpose": purpose,
        "status": "open",
        "created_at": str(utcnow()),
    }
    tickets[str(channel_id)] = ticket
    await save_tickets(tickets)
    return ticket


async def claim_ticket(channel_id: int, staff_id: int) -> bool:
    tickets = await load_tickets()
    ticket = tickets.get(str(channel_id))

    if not ticket:
        return False

    if ticket["claimer_id"] is not None:
        return False

    ticket["claimer_id"] = staff_id
    await save_tickets(tickets)
    return True


async def transfer_ticket(
    channel_id: int, staff_id: int, new_staff_id: int
) -> bool:
    tickets = await load_tickets()
    ticket = tickets.get(str(channel_id))

    if not ticket:
        return False
    if ticket["claimer_id"] != staff_id:
        return False
    ticket["claimer_id"] = new_staff_id
    await save_tickets(tickets)
    return True


async def close_ticket(channel_id: int, staff_id: int) -> bool:
    tickets = await load_tickets()
    ticket = tickets.get(str(channel_id))
    if not ticket:
        return False
    if ticket["claimer_id"] != staff_id:
        return False
    ticket["status"] = "closed"
    await save_tickets(tickets)
    return True


async def is_ticket(channel_id: int) -> bool:
    tickets = await load_tickets()
    return str(channel_id) in tickets


async def get_ticket_owner(channel_id: int) -> Optional[int]:
    ticket = await get_ticket(channel_id)
    if not ticket:
        return None
    return ticket["owner_id"]


async def get_ticket_claimer(channel_id: int) -> Optional[int]:
    ticket = await get_ticket(channel_id)
    if not ticket:
        return None
    return ticket["claimer_id"]


async def is_ticket_claimed(channel_id: int) -> bool:
    ticket = await get_ticket(channel_id)
    return bool(ticket and ticket["claimer_id"] is not None)


async def is_ticket_open(channel_id: int) -> bool:
    ticket = await get_ticket(channel_id)
    return bool(ticket and ticket["status"] == "open")


async def get_ticket_status(channel_id: int) -> Optional[str]:
    ticket = await get_ticket(channel_id)
    if not ticket:
        return None
    return ticket["status"]


async def get_ticket_purpose(channel_id: int) -> Optional[str]:
    ticket = await get_ticket(channel_id)
    if not ticket:
        return None
    return ticket["selected_purpose"]


async def get_ticket_time(channel_id: int) -> Optional[str]:
    ticket = await get_ticket(channel_id)
    if not ticket:
        return None
    return ticket["created_at"]


async def get_all_tickets():
    tckts = await load_tickets()
    return tckts.copy()


async def get_tickets_count():
    return len(await load_tickets())


async def get_tickets_count_for_user(user_id: int):
    tickets = await load_tickets()
    owner_to_check = user_id
    open_count = sum(
        1
        for ticket in tickets.values()
        if ticket["owner_id"] == owner_to_check
        and ticket["status"] in ["open", "inactive"]
    )
    return open_count


async def get_any_tickets_count_for_user(user_id: int):
    tickets = await load_tickets()
    owner_to_check = user_id
    any_count = sum(
        1
        for ticket in tickets.values()
        if ticket["owner_id"] == owner_to_check
    )
    return any_count
