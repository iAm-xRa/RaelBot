# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details:

#     https://www.gnu.org/licenses/gpl-3.0.txt

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import discord
from discord.ext import commands
import os
import sys
from dotenv import load_dotenv
from utils.logger import setup_logger
from utils.config import load_config
from ui.views.TicketPanelView import TicketPanelView
from ui.views.TicketModView import TicketModView, TransferView
from ui.views.ReviewPanelView import ReviewPanelView

if sys.version_info < (3, 10):
    sys.exit("Python 3.10 or higher is required to run RaelBot.")

botlogger = setup_logger()

load_dotenv()
token = os.getenv("bot_token")

if not token:
    botlogger.critical("Token is not found or is invalid.")
    raise RuntimeError("Invalid Token")

botconfig = load_config()


class RaelBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=botconfig.prefix,
            intents=intents,
            activity=discord.Activity(
                type=discord.ActivityType.playing, name=botconfig.bot_activity
            ),
            status=getattr(discord.Status, botconfig.bot_activity_type, None),
            help_command=None,
        )

    async def setup_hook(self):
        botlogger.info("Starting setup_hook.")
        extensions = [
            "cogs.admin",
            "cogs.general_commands",
            "cogs.embeds.embed_builder",
            "cogs.tickets.tickets",
            "cogs.tickets.inactivity",
            "cogs.welcome",
            "cogs.errors",
        ]
        self.add_view(TicketPanelView())
        botlogger.info("Added the ticket panel view.")

        self.add_view(TicketModView())
        botlogger.info("Added the ticket mod view.")

        self.add_view(TransferView())
        botlogger.info("Added the transfer ticket view.")

        self.add_view(ReviewPanelView())
        botlogger.info("Added the review view.")

        for ext in extensions:
            try:
                await self.load_extension(ext)
                botlogger.info(f"Loaded cog : {ext}")
            except Exception as e:
                botlogger.exception(f"Failed to load cog : {ext}\n{e}")

        guild = discord.Object(id=botconfig.guild_id)
        botlogger.info("Clearing the commands cache from the tree.")
        self.tree.clear_commands(guild=guild)
        self.tree.copy_global_to(guild=guild)
        botlogger.info("Syncing App Commands.")
        await self.tree.sync(guild=guild)

    async def on_ready(self):
        botlogger.info(f"Logged in as {self.user} ID : ({self.user.id})")


bot = RaelBot()
bot.run(token)
