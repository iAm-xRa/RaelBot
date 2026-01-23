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
from utils import embeds
from utils import config
from ui.views.TicketModView import TicketModView

botlogger = logging.getLogger("bot")
botconfig = config.load_config()


class TicketBuyModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=botconfig.ticket_modal_title)
        self.product = discord.ui.TextInput(
            label=botconfig.ticket_modal_label1,
            max_length=24,
            placeholder=botconfig.ticket_modal_place_holder1,
            min_length=3,
        )

        self.details = discord.ui.TextInput(
            label=botconfig.ticket_modal_label2,
            style=discord.TextStyle.paragraph,
            required=False,
            max_length=400,
        )

        self.add_item(self.product)
        self.add_item(self.details)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        count_usr = await tickets.get_tickets_count_for_user(
            interaction.user.id
        )
        if count_usr >= botconfig.max_user_tickets:
            await interaction.followup.send(
                embed=embeds.TCKT_LMT_USR,
                ephemeral=True
            )
            return

        count_guild = await tickets.get_tickets_count()
        if count_guild >= botconfig.tickets_limit:
            await interaction.followup.send(
                embed=embeds.TCKT_LMT_SRVR,
                ephemeral=True
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
                discord.NotFound
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
            except (
                discord.Forbidden,
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
                name=(
                    f"❖ {botconfig.first_purpose}-"
                    f"{interaction.user.name.replace('.', '-').replace('_', '-').lower()}"
                ),
                category=category,
                overwrites={
                    interaction.guild.default_role:
                        discord.PermissionOverwrite(
                            view_channel=False
                        ),
                    interaction.user:
                        discord.PermissionOverwrite(
                            send_messages=True,
                            view_channel=True
                        ),
                    support:
                        discord.PermissionOverwrite(
                            send_messages=True,
                            view_channel=True
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
            channel_id=channel.id,
            owner_id=interaction.user.id,
            purpose=str(botconfig.first_purpose),
        )

        fields = [
            (
                botconfig.purpose1_field1,
                f"`{self.product.value.strip()}`",
                True
            ),
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
        if self.details.value:
            fields.append(
                (
                    botconfig.purpose1_field2,
                    f"`{self.details.value.strip()}`",
                    False
                )
            )

        purpose = botconfig.first_purpose.capitalize()
        ticket_embed = embeds.create_embed(
            title=f"***{purpose} Ticket Created By {interaction.user.name}***",
            description=botconfig.purpose1_embed_description,
            thumbnail=interaction.user.display_avatar.url,
            image=botconfig.purpose1_embed_image,
            fields=fields,
            replace=True,
            placeholders=(
                interaction.user.name,
                interaction.user.display_name,
                interaction.guild.name,
            ),
        )

        msg = None
        mention = f"||<@&{botconfig.support_role_id}>||"
        try:
            msg = await channel.send(
                embed=ticket_embed,
                view=TicketModView(),
                content=f"***{mention} {purpose} Ticket Created By {interaction.user.mention}***",
            )

        except (discord.HTTPException, discord.Forbidden) as e:
            botlogger.error(
                f"Couldn't send message to ticket : {channel.id}\n{e}"
            )

        all_tickets, ticket = await tickets.get_tickets_and_ticket(channel.id)
        if msg:
            ticket["message_id"] = msg.id if msg.id else None
        await tickets.save_tickets(all_tickets)
        await interaction.followup.send(embed=embeds.EMBD_SCCS, ephemeral=True)
        botlogger.info(
            f"Created ticket with id ({channel.id}) and name ({channel.name})."
        )
