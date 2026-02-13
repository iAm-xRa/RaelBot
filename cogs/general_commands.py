# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import asyncio
from discord.ext import commands
from utils import embeds


class GeneralCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(
        name="about",
        description="Show info about RaelBot!"
    )
    async def about_cmd(self, ctx: commands.Context):
        msg = await ctx.send(embed=embeds.ABOUT_EMBED)

async def setup(bot: commands.Bot):
    await bot.add_cog(GeneralCommands(bot))
