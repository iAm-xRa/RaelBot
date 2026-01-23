# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


from datetime import datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def discord_timestamp() -> datetime:
    return utcnow()
