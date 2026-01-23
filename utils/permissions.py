# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


from discord.ext import commands
from utils.config import load_config

bot_config = load_config()


def is_admin():
    async def predicate(ctx: commands.Context):
        if not ctx.guild:
            return False
        return any(
            role.id == bot_config.admin_role_id
            for role in ctx.author.roles
        )

    return commands.check(predicate)


def is_support():
    async def predicate(ctx: commands.Context):
        if not ctx.guild:
            return False
        return any(
            role.id == bot_config.support_role_id for role in ctx.author.roles
        )

    return commands.check(predicate)
