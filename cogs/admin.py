# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


from discord.ext import commands
import logging
import discord
from utils import embeds
from utils.config import load_config
from utils.permissions import is_admin
from ui.views.TicketPanelView import TicketPanelView
from ui.views.ReviewPanelView import ReviewPanelView

botlogger = logging.getLogger("bot")


async def handle_admin_checkfailure(ctx: commands.Context):
    ping_error_embed = embeds.MISSING_PERM
    msg: discord.Message = await ctx.send(
        embed=ping_error_embed,
        ephemeral=True
        )
    await msg.delete(delay=5)


class AdminOnly(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot_config = load_config()

    @commands.hybrid_command(name="ping", description="Check if I'm alive.")
    @commands.guild_only()
    @is_admin()
    async def ping(self, ctx: commands.Context):
        botlogger.info(
            f"Ping command executed by {ctx.author} (ID : {ctx.author.id}) in {ctx.guild.name if ctx.guild else "DMs"}"
        )
        pingembed = embeds.create_embed(
            title="Pong!",
            description=f"**My Latency is {round(self.bot.latency * 1000)} ms !**\n`Just a reminder, this command is admin only !`",
        )
        await ctx.send(embed=pingembed)

    @ping.error
    async def ping_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            ping_error_embed = embeds.MISSING_PERM
            ping_error_embed.description = "**Hey you are not an admin !**\n`But since I caught you anyways, pong.`"
            msg = await ctx.send(embed=ping_error_embed, ephemeral=True)
            await msg.delete(delay=5)

    @commands.hybrid_command(
        name="deploy_ticket_panel", description="Deploy the ticket panel !"
    )
    @commands.guild_only()
    @is_admin()
    async def deploy_ticket(self, ctx: commands.Context):
        view = TicketPanelView()
        embedtosend = embeds.TICK_PNLEMB
        await ctx.send(embed=embedtosend, view=view)
        botlogger.info(f"Ticket panel deployed by {ctx.author} in {ctx.guild.name}")

    @deploy_ticket.error
    async def ticket_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await handle_admin_checkfailure(ctx)

    @commands.hybrid_command(
        name="deploy_review_panel", description="Deploy the review panel !"
    )
    @commands.guild_only()
    @is_admin()
    async def deploy_review(self, ctx: commands.Context):
        view = ReviewPanelView()
        embedtosend = embeds.REVIEW_EMBD
        await ctx.send(view=view, embed=embedtosend)
        botlogger.info(f"Review panel deployed by {ctx.author} in {ctx.guild.name}")

    @deploy_review.error
    async def review_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await handle_admin_checkfailure(ctx)


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminOnly(bot))
