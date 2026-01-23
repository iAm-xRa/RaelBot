# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
import logging
from discord.ext import commands, tasks
from utils import tickets, embeds, config, permissions

botconfig = config.load_config()
botlogger = logging.getLogger("bot")


class TicketModCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.inactive_ensure.start()
        self.active_ensure.start()

    @commands.hybrid_command(
        name="add", description="Add a member to the current ticket"
    )
    @commands.guild_only()
    @permissions.is_support()
    async def add_member(self, ctx: commands.Context, member: discord.Member):
        current_ticket = await tickets.get_ticket(ctx.channel.id)
        if not current_ticket:
            await ctx.send(embed=embeds.NOT_TCKT, ephemeral=True)
            return
        elif ctx.author.id != current_ticket["claimer_id"]:
            await ctx.send(embed=embeds.NOT_CLMR, ephemeral=True)
            return
        elif ctx.author.bot:
            await ctx.send(embed=embeds.NO_BOTS, ephemeral=True)
            return
        await ctx.channel.set_permissions(
            member,
            send_messages=True,
            view_channel=True
            )
        await ctx.send(
            embed=embeds.create_embed(
                title="***Member added !***",
                description=f"`Added` {member.mention} `to the ticket !`",
            )
        )

    @add_member.error
    async def add_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            ping_error_embed = embeds.MISSING_PERM
            ping_error_embed.description = (
                "`Hey you are not a staff !\n You can't execute this command`"
            )
            msg = await ctx.send(embed=ping_error_embed, ephemeral=True)
            await msg.delete(delay=5)

    @commands.hybrid_command(
        name="remove", description="Remove a member from the current ticket"
    )
    @commands.guild_only()
    @permissions.is_support()
    async def remove_member(
        self,
        ctx: commands.Context,
        member: discord.Member
    ):
        current_ticket = await tickets.get_ticket(ctx.channel.id)
        if not current_ticket:
            await ctx.send(embed=embeds.NOT_TCKT, ephemeral=True)
            return
        elif ctx.author.id != current_ticket["claimer_id"]:
            await ctx.send(embed=embeds.NOT_CLMR, ephemeral=True)
            return
        elif ctx.author.bot:
            await ctx.send(embed=embeds.NO_BOTS, ephemeral=True)
            return
        elif ctx.author.id == member.id:
            await ctx.send(embed=embeds.NO_SELF_REMOVE, ephemeral=True)
            return
        await ctx.channel.set_permissions(
            member, send_messages=False, view_channel=False
        )
        await ctx.send(
            embed=embeds.create_embed(
                description=f"***Removed {member.mention} !***",
                title="***Member removed !***",
            )
        )

    @remove_member.error
    async def remove_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.CheckFailure):
            ping_error_embed = embeds.MISSING_PERM
            ping_error_embed.description = (
                "`Hey you are not a staff !\n You can't execute this command`"
            )
            msg = await ctx.send(embed=ping_error_embed, ephemeral=True)
            await msg.delete(delay=5)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        all_tickets, ticket = await tickets.get_tickets_and_ticket(
            channel_id=channel.id
        )  # Both are dict
        if ticket:
            ticket["status"] = "closed"
            await tickets.save_tickets(all_tickets)
            member = channel.guild.get_member(ticket["owner_id"])
            if member:
                try:
                    await member.send(
                        embed=embeds.create_embed(
                            title=f"***Notification from {channel.guild.name}***",
                            description=f"`Your ticket {channel.name} was closed..`",
                        ),
                        content=f"{member.mention}",
                    )
                except (discord.Forbidden, discord.HTTPException) as e:
                    botlogger.error(f"Couldn't dm member : {member.name}\n{e}")
            botlogger.info(
                f"{channel.name} ({channel.id}) has been deleted and was marked as a Closed ticket."
            )

    @tasks.loop(minutes=5)
    async def inactive_ensure(self):
        category = self.bot.get_channel(botconfig.inactive_tickets_category)
        if category:
            for channel in category.text_channels:
                all_tickets, ticket = await tickets.get_tickets_and_ticket(
                    channel_id=channel.id
                )
                if ticket and ticket["status"] not in ["inactive", "closed"]:
                    ticket["status"] = "inactive"
                    await tickets.save_tickets(all_tickets)
                    botlogger.info(
                        f"Ticket {channel.name} ({channel.id}) has been marked as Inactive."
                    )
                    await embeds.update_ticket_embed_field(
                        channel,
                        ticket["message_id"],
                        "***Ticket Status***",
                        "inactive"
                    )
                    owner = channel.guild.get_member(ticket["owner_id"])
                    if owner:
                        try:
                            await owner.send(
                                embed=embeds.create_embed(
                                    title=f"***Notification from {channel.guild.name}***",
                                    description=f"`Your ticket {channel.name} was waitlisted..`",
                                ),
                                content=f"{owner.mention}",
                            )
                        except (discord.Forbidden, discord.HTTPException):
                            botlogger.warning(f"Could not DM {owner}.")
                            continue
                    await channel.send(embed=embeds.WAITLISTED)

    @inactive_ensure.before_loop
    async def before_inactive_ensure(self):
        await self.bot.wait_until_ready()

    @tasks.loop(minutes=6)
    async def active_ensure(self):
        category = self.bot.get_channel(botconfig.active_tickets_category)
        if category:
            for channel in category.text_channels:
                all_tickets, ticket = await tickets.get_tickets_and_ticket(
                    channel_id=channel.id
                )
                if ticket and ticket["status"] != "open":
                    ticket["status"] = "open"
                    await tickets.save_tickets(all_tickets)
                    botlogger.info(
                        f"Ticket {channel.name} ({channel.id}) has been marked as Open."
                    )
                    await embeds.update_ticket_embed_field(
                        channel,
                        ticket["message_id"],
                        "***Ticket Status***",
                        "open"
                    )

    @active_ensure.before_loop
    async def before_active_ensure(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketModCog(bot))
