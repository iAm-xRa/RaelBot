# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
import logging
from utils import tickets
from ui.modals.ticket_create import TicketBuyModal
from utils.config import load_config
from utils import embeds
from ui.views.TicketModView import TicketModView


botconfig = load_config()
botlogger = logging.getLogger("bot")


class TicketPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.selected_purpose: str | None = None

    @discord.ui.select(
        placeholder=botconfig.t_placeholder,
        options=[
            discord.SelectOption(
                label=botconfig.t_label1,
                value=str(botconfig.first_purpose),
                description=botconfig.t_description1,
            ),
            discord.SelectOption(
                label=botconfig.t_label2,
                value=str(botconfig.second_purpose),
                description=botconfig.t_description2,
            ),
        ],
        custom_id="ticket:select",
    )
    async def ticket_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        self.selected_purpose = select.values[0]
        await interaction.response.defer(ephemeral=True)

    @discord.ui.button(
        style=discord.ButtonStyle.primary,
        label="Create Ticket",
        custom_id="ticket:create:button",
    )
    async def create_ticket(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        if not self.selected_purpose:
            await interaction.response.send_message(
                embed=embeds.MISSING_SELECT, ephemeral=True
            )
            return

        if self.selected_purpose == botconfig.first_purpose:
            await interaction.response.send_modal(TicketBuyModal())
            return

        if self.selected_purpose == botconfig.second_purpose:
            await interaction.response.defer(ephemeral=True)

            count_user = await tickets.get_tickets_count_for_user(
                interaction.user.id
            )
            if count_user >= botconfig.max_user_tickets:
                await interaction.followup.send(
                    embed=embeds.TCKT_LMT_USR, ephemeral=True
                )
                return

            count_guild = await tickets.get_tickets_count()
            if count_guild >= botconfig.tickets_limit:
                await interaction.followup.send(
                    embed=embeds.TCKT_LMT_SRVR, ephemeral=True
                )
                return

            category = interaction.guild.get_channel(
                botconfig.active_tickets_category
            )

            if not category:
                try:
                    category = await interaction.guild.fetch_channel(
                        botconfig.active_tickets_category
                    )
                except (
                    discord.Forbidden,
                    discord.HTTPException,
                    discord.NotFound,
                ) as e:
                    await interaction.followup.send(
                        embed=embeds.CHANNEL_ERR, ephemeral=True
                    )
                    botlogger.error(
                        f"Couldn't find the active tickets category.\n{e}"
                    )
                    return

            support = interaction.guild.get_role(botconfig.support_role_id)
            if not support:
                try:
                    support = await interaction.guild.fetch_role(
                        botconfig.support_role_id
                    )
                except (discord.Forbidden,
                        discord.NotFound,
                        discord.HTTPException
                    ):
                    await interaction.followup.send(
                        embed=embeds.CHANNEL_ERR, ephemeral=True
                    )
                    botlogger.error("Couldn't find the support role.")
                    return
            try:
                channel = await interaction.guild.create_text_channel(
                    name=f"★ {botconfig.second_purpose}-{interaction.user.name.replace(".", "-").replace("_", "-").lower()}",
                    category=category,
                    overwrites={
                        interaction.guild.default_role: discord.PermissionOverwrite(
                            view_channel=False
                        ),
                        interaction.user: discord.PermissionOverwrite(
                            send_messages=True, view_channel=True
                        ),
                        support: discord.PermissionOverwrite(
                            send_messages=True, view_channel=True
                        ),
                    },
                )
            except (discord.Forbidden,
                    discord.HTTPException,
                    discord.NotFound
                    ) as e:
                await interaction.followup.send(
                    embed=embeds.CHANNEL_ERR, ephemeral=True
                )
                botlogger.error(
                    f"Couldn't create channel for member : {interaction.user.name} !\n{e}"
                )
                return

            ticket_created = await tickets.create_ticket(
                channel.id,
                interaction.user.id,
                purpose=botconfig.second_purpose
            )

            fields = [
                (
                    "***Ticket Status***",
                    f"{ticket_created['status']}",
                    True
                ),
                (
                    "***Ticket Purpose***",
                    f"{ticket_created['selected_purpose']}",
                    True
                ),
            ]
            purpose = botconfig.second_purpose.capitalize()
            ticket_embed = embeds.create_embed(
                title=f"***{purpose} Ticket Created By {interaction.user.name}***",
                description=botconfig.purpose2_embed_description,
                thumbnail=interaction.user.display_avatar.url,
                image=botconfig.purpose2_embed_image,
                fields=fields,
            )
            msg = None
            metion = f"||<@&{botconfig.support_role_id}>||"
            try:
                msg = await channel.send(
                    content=f"***{metion} {purpose} Ticket Created By {interaction.user.mention}***",
                    embed=ticket_embed,
                    view=TicketModView(),
                )
            except (discord.HTTPException, discord.Forbidden) as e:
                botlogger.error(
                    f"Couldn't send message to ticket : {channel.id}\n{e}"
                )

            all_tickets, ticket = await tickets.get_tickets_and_ticket(
                channel_id=channel.id
            )
            if msg:
                ticket["message_id"] = msg.id if msg.id else None
            await tickets.save_tickets(all_tickets)
            await interaction.followup.send(
                embed=embeds.EMBD_SCCS,
                ephemeral=True
            )
            botlogger.info(
                f"Created ticket with id ({channel.id})."
            )
