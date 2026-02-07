# RaelBot - Discord bot for ticket systems.
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
from discord.ext import commands
import logging
from utils import embeds
from utils.config import load_config
from utils.permissions import is_admin

botlogger = logging.getLogger("bot")


class EmbedBuilderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot_config = load_config()

    @commands.hybrid_command(
            name="create_embed",
            description="I will create a custom embed for you and send it wherever you want !"
        )
    @commands.guild_only()
    @is_admin()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def create_embed(
        self,
        ctx: commands.Context,
        channel_to_send: discord.TextChannel = None,
        title: str = None,
        description: str = None,
        footer_text: str = None
    ):
        """Create an embed and send it to a channel (Admin only)"""

        if not ctx.interaction:
            sorry_embed = embeds.PRFX_CMD_WARN
            await ctx.send(embed=sorry_embed)
            return

        if not all((channel_to_send, title, description)):
            missing_arg_embed = embeds.create_embed(
                title="Missing Argument/s !",
                description="`Make sure you have provided me with the embed's title, description, and channel_to_send !`",
                color=self.bot_config.default_embed_error_color
            )

            await ctx.send(embed=missing_arg_embed, ephemeral=True)
            return

        else:
            botlogger.info(
                f"Create Embed executed by {ctx.author} (ID : {ctx.author.id})"
            )  # DMs not possible
            created_embed = embeds.create_embed(
                title=title,
                description=description.replace("<newline>", "\n"),
                footer=footer_text or self.bot_config.default_footer_text
            )
            try:
                await channel_to_send.send(embed=created_embed)
            except discord.Forbidden:
                await ctx.send(embed=embeds.CORD_FORBIDDEN, ephemeral=True)
                return
            success_embed = embeds.create_embed(
                title="Successfully created your embed !",
                description=f"*I sent your embed to <#{channel_to_send.id}> !*\n`Just a reminder, this command is admin only !`"
            )
            await ctx.send(embed=success_embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(EmbedBuilderCog(bot))
