# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


from discord.ext import tasks, commands
import discord
from utils import tickets
import datetime
from utils.config import load_config
import logging

botlogger = logging.getLogger("bot")
botconfig = load_config()


class InactivityCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.inactive.start()

    def cog_unload(self):
        self.inactive.cancel()

    @tasks.loop(minutes=botconfig.inactivity_loop_interval)
    async def inactive(self) -> None:
        botlogger.info("Starting inactivity loop...")
        all_tickets: dict = await tickets.get_all_tickets()
        for ticket in all_tickets.items():
            tckt_chnl_id = ticket[0]
            try:
                tckt_chnl: discord.TextChannel = await self.bot.fetch_channel(
                    tckt_chnl_id
                )
            except (discord.NotFound, discord.HTTPException):
                tckt_chnl: discord.TextChannel = self.bot.get_channel(
                    tckt_chnl_id
                )

            if not tckt_chnl:
                continue

            tickets_dict, crnt_tckt = await tickets.get_tickets_and_ticket(
                tckt_chnl_id
            )
            if (
                crnt_tckt["status"] in {"inactive", "closed"}
                or tckt_chnl.category_id == self.inactive_category.id
            ):
                continue

            if not tckt_chnl.last_message_id:
                continue

            last_msg = None
            try:
                last_msg = await tckt_chnl.fetch_message(
                    tckt_chnl.last_message_id
                )
            except (discord.NotFound, AttributeError):
                async for msg in tckt_chnl.history(limit=1):
                    last_msg = msg
            except discord.Forbidden:
                botlogger.error(f"No permissions to read {tckt_chnl.name}..")
                continue

            if not last_msg:
                continue

            last_msg_time = last_msg.created_at
            current_time = datetime.datetime.now(datetime.timezone.utc)
            difference_time = current_time - last_msg_time

            if (
                difference_time.total_seconds() > botconfig.inactive_after * 60
            ):  # Convert both values to seconds
                if not self.inactive_category:
                    botlogger.error(
                        "Inactive category not found, skipping ticket processing."
                    )
                    continue
                await tckt_chnl.edit(category=self.inactive_category)
                crnt_tckt["status"] = "inactive"
                await tickets.save_tickets(tickets_dict)
                botlogger.info(
                    f"Moved inactive ticket {tckt_chnl.name} to the inactive tickets category."
                )
        botlogger.info("Finished inactivity loop.")

    @inactive.before_loop
    async def before_inactive(self):
        await self.bot.wait_until_ready()
        self.inactive_category = await self.bot.fetch_channel(
            botconfig.inactive_tickets_category
        )
        if not self.inactive_category:
            self.inactive_category = self.bot.get_channel(
                botconfig.inactive_tickets_category
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(InactivityCog(bot))
