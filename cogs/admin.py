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
from utils import tickets
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

    @commands.hybrid_command(
        name="add_to_blacklist", description="Blacklists a member from using tickets and submitting reviews!"
    )
    @commands.guild_only()
    @is_admin()
    async def add_blacklist(self, ctx: commands.Context, member: discord.Member):
        if member and member.id:
            if member.bot:
                await ctx.send(embed=embeds.NO_BOT_BLACKLIST, ephemeral=True)
                return
            elif member.id == ctx.author.id:
                await ctx.send(embed=embeds.NO_SELF_BLACKLIST, ephemeral=True)
                return
            elif ctx.guild.get_role(self.bot_config.admin_role_id) in member.roles:
                await ctx.send(embed=embeds.NO_ADMIN_BLACKLIST, ephemeral=True)
                return

            blacklisted = await tickets.add_blacklist(member.id)
            embedtosend = embeds.create_embed(
                title="***Member Successfully Blacklisted!***",
                description=f"*{member.mention}* `has been added to the blacklist`\n`They won't be able to create tickets or submit reviews!`",
                thumbnail=member.avatar.url if member.avatar else None
            )
            if blacklisted:
                await ctx.send(embed=embedtosend)
                botlogger.info(f"{ctx.author.name} ({ctx.author.id}) has blacklisted {member.name} ({member.id})")
            else:
                embedtosend = embeds.ALREADY_BLACKLISTED
                await ctx.send(embed=embedtosend, ephemeral=True)

    @add_blacklist.error
    async def addblacklist_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await handle_admin_checkfailure(ctx)

    @commands.hybrid_command(
        name="remove_from_blacklist", description="Removes a member from the blacklist, allowing them to create tickets and submit reveiws."
    )
    @is_admin()
    async def remove_blacklist(self, ctx:commands.Context, member: discord.Member):
        if member.bot:
            await ctx.send(embed=embeds.BOT_REMOVE_BLACKLIST, ephemeral=True)
            return
        removed = await tickets.remove_blacklist(str(member.id))
        if removed:
            embedtosend = embeds.create_embed(
                title="***Member removed from the blacklist!***",
                description=f"*{member.mention}* `will be able to create tickets and submit reviews from now on!`",
                thumbnail=member.avatar.url if member.avatar else None
            )
            botlogger.info(f"{ctx.author.name} ({ctx.author.id}) has removed {member.name} ({member.id}) from the blacklist.")
        else:
            embedtosend = embeds.create_embed(
                "***This member is not blacklisted!***",
                description=f"*{member.mention}* `is not in the blacklist`",
                thumbnail=member.avatar.url if member.avatar else None
            )
        await ctx.send(embed=embedtosend)
    
    @remove_blacklist.error
    async def removeblacklist_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await handle_admin_checkfailure(ctx)

    @commands.hybrid_command(
        name="help", description="Sends an embed that shows how the bot works."
    )
    @is_admin()
    async def help_cmd(self, ctx:commands.Context):
        if not ctx.interaction:
            sorry_embed = embeds.PRFX_CMD_WARN
            await ctx.send(embed=sorry_embed)
            return
        await ctx.send(embed=embeds.HELP, ephemeral=True)
    
    @help_cmd.error
    async def removeblacklist_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            await handle_admin_checkfailure(ctx)

async def setup(bot: commands.Bot):
    await bot.add_cog(AdminOnly(bot))
