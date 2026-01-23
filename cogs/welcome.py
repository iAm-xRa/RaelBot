# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


from discord.ext import commands
import discord
import logging
from utils import embeds
from utils.config import load_config

botlogger = logging.getLogger("bot")


class WelcomeCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.botconfig = load_config()
        self.wlcm_chnl: discord.TextChannel | None = None
        self.send = True

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.botconfig.welcome_channel:
            self.send = False
            return
        self.wlcm_chnl = self.bot.get_channel(self.botconfig.welcome_channel)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if self.send:
            if not member.guild:
                return

            if member.bot:
                return

            if self.wlcm_chnl is None:
                self.wlcm_chnl = await self.bot.fetch_channel(
                    self.botconfig.welcome_channel
                )

            if self.wlcm_chnl:
                embed_title = self.botconfig.welcome_title
                embed_cntnt = self.botconfig.welcome_content

                wlcm_embed = embeds.create_embed(
                    title=embed_title,
                    description=embed_cntnt,
                    color=self.botconfig.welcome_color,
                    image=self.botconfig.welcome_image,
                    thumbnail=member.avatar.url if member.avatar else None,
                    replace=True,
                    placeholders=(
                        member.name,
                        member.display_name,
                        member.guild.name
                    ),
                )
                try:
                    await self.wlcm_chnl.send(
                        content=f"*Welcome, {member.mention}*",
                        embed=wlcm_embed
                    )
                except (discord.Forbidden, discord.NotFound) as e:
                    botlogger.error(
                        f"Could not send the welcome message to {self.wlcm_chnl.name}\n{e}"
                    )

                if not self.botconfig.member_role_id:
                    return

                memb_role = member.guild.get_role(
                    self.botconfig.member_role_id
                )

                if not memb_role:
                    botlogger.error("Member role could not be found..")
                    return
                try:
                    await member.add_roles(
                        memb_role,
                        reason="Auto role on join.."
                    )
                except (discord.Forbidden, discord.NotFound) as e:
                    botlogger.error(
                        f"Could not add the member role to {member.name}\n{e}"
                    )

            else:
                botlogger.error("Welcome channel could not be found..")


async def setup(bot: commands.Bot):
    await bot.add_cog(WelcomeCog(bot))
