# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
from utils.config import load_config
from utils import timestmp
from utils import embeds
import asyncio
from utils import tickets
import io

botconfig = load_config()


class TicketModView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim", style=discord.ButtonStyle.green, custom_id="claim"
    )
    async def claim_btn(self, interaction: discord.Interaction, button: discord.Button):
        if (
            interaction.guild.get_role(botconfig.support_role_id)
            in interaction.user.roles
        ):
            tickets_dict, claimed_ticket = await tickets.get_tickets_and_ticket(
                interaction.channel_id
            )
            if claimed_ticket:
                if not claimed_ticket["claimer_id"]:
                    claimed_ticket["claimer_id"] = interaction.user.id
                    await tickets.save_tickets(tickets_dict)
                    await interaction.channel.set_permissions(
                        interaction.user, send_messages=True, view_channel=True
                    )
                    await interaction.channel.set_permissions(
                        interaction.guild.get_role(botconfig.support_role_id),
                        send_messages=False,
                        view_channel=True,
                    )
                    embd = embeds.create_embed(
                        title="***This ticket has been claimed***",
                        description=f"*The staff handling your ticket is {interaction.user.mention} !*",
                        thumbnail=interaction.user.avatar.url if interaction.user.avatar else None,
                    )
                    await interaction.response.send_message(embed=embd)
                else:
                    embd = embeds.create_embed(
                        title="***Couldn't perform this action..***",
                        description="*This ticket is already claimed...*",
                    )
                    await interaction.response.send_message(
                        embed=embd,
                        ephemeral=True
                    )

            else:
                await interaction.response.send_message(
                    "*This is no longer a ticket I assume..*", ephemeral=True
                )
        else:
            await interaction.response.send_message(
                embed=embeds.MISSING_PERM, ephemeral=True
            )

    @discord.ui.button(
        label="Transfer", style=discord.ButtonStyle.grey, custom_id="trnsfr"
    )
    async def trnsfr_btn(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.send_message(
            view=TransferView(),
            ephemeral=True
        )

    @discord.ui.button(
        label="Close", style=discord.ButtonStyle.danger, custom_id="close"
    )
    async def close_btn(self, interaction: discord.Interaction, button: discord.Button):
        if (
            interaction.guild.get_role(botconfig.support_role_id)
            in interaction.user.roles
        ):
            tickets_dict, closed_ticket = await tickets.get_tickets_and_ticket(
                interaction.channel_id
            )
            if closed_ticket:
                if closed_ticket["claimer_id"] == interaction.user.id:
                    await interaction.response.send_message(
                        "`Generating ticket transcript..`", ephemeral=True
                    )
                    closed_ticket["status"] = "closed"
                    await tickets.save_tickets(tickets_dict)
                    messages = [
                        message
                        async for message in interaction.channel.history(
                            limit=None, oldest_first=True
                        )
                    ]
                    output = f"Transcript for {interaction.channel.name} ({interaction.channel.id}) !\nExported on {timestmp.utcnow()}\n{'*'*50}\n\n"
                    for msg in messages:
                        msg_timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S")
                        msg_content = msg.content
                        if not msg_content and msg.embeds:
                            msg_content = "[ EMBED CONTENT ]"
                        output += f"[{msg_timestamp}] {msg.author.name} ({msg.author.id}): {msg_content}\n"
                        if msg.attachments:
                            output += f"    [ATTACHMENT: {msg.attachments[0].url}]\n"
                    final_output_file = io.BytesIO(output.encode("utf-8"))
                    transcripts_channel = interaction.guild.get_channel(
                        botconfig.transcript_channel
                    )
                    if transcripts_channel:
                        trnscrpt_embed = embeds.create_embed(
                            title="***Ticket Logged***",
                            timestamp=True,
                            thumbnail=interaction.user.avatar.url if interaction.user.avatar else None,
                        )
                        trnscrpt_embed.add_field(
                            name="`Ticket Name`",
                            value=f"`{interaction.channel.name}`",
                            inline=True,
                        )
                        trnscrpt_embed.add_field(
                            name="`Ticket Id`",
                            value=f"`{interaction.channel_id}`",
                            inline=True,
                        )
                        trnscrpt_embed.add_field(
                            name="`Closed By`",
                            value=f"{interaction.user.mention}",
                            inline=True,
                        )
                        file_trnscrpt = discord.File(
                            final_output_file,
                            filename=f"transcript-{interaction.channel.name}.txt",
                        )
                        await transcripts_channel.send(
                            embed=trnscrpt_embed, file=file_trnscrpt
                        )
                    await interaction.channel.send(
                        embed=embeds.create_embed(
                            title="***Ticket closed***",
                            description="`Ticket will be deleted in 5 seconds..`",
                        )
                    )
                    await asyncio.sleep(5)
                    await interaction.channel.delete()
                else:
                    await interaction.response.send_message(
                        "`You are not the claimer to close this ticket.`",
                        ephemeral=True,
                    )
            else:
                embd = embeds.create_embed(
                    title="***Couldn't perform this action..***",
                    description="`This is not a ticket..`",
                )
                await interaction.response.send_message(
                    embed=embd,
                    ephemeral=True
                )
        else:
            await interaction.response.send_message(embed=embeds.MISSING_PERM)


class TransferSelect(discord.ui.UserSelect):
    def __init__(self):
        super().__init__(
            max_values=1,
            min_values=1,
            placeholder="Select the staff you want to transfer the ticket to.",
            custom_id="trnsfr:select",
        )

    async def callback(self, interaction: discord.Interaction):
        target_staff: discord.Member = self.values[0]
        staff_role = interaction.guild.get_role(botconfig.support_role_id)
        if staff_role in interaction.user.roles:
            tickets_dict, trnsfrd_ticket = await tickets.get_tickets_and_ticket(
                interaction.channel_id
            )
            if trnsfrd_ticket:
                if trnsfrd_ticket["claimer_id"] == interaction.user.id:
                    if (
                        staff_role in target_staff.roles
                        and not target_staff.bot
                        and target_staff.id != interaction.user.id
                    ):
                        await interaction.channel.set_permissions(
                            target_staff, send_messages=True, view_channel=True
                        )
                        await interaction.channel.set_permissions(
                            staff_role, send_messages=False, view_channel=True
                        )
                        await interaction.channel.set_permissions(
                            interaction.user, send_messages=False,
                            view_channel=True
                        )
                        trnsfrd_ticket["claimer_id"] = target_staff.id
                        await tickets.save_tickets(tickets_dict)
                        await interaction.response.send_message(
                            embed=embeds.create_embed(
                                title="***This ticket has been transfered !***",
                                description=f"`New staff handling the ticket is: `{target_staff.mention}",
                                thumbnail=target_staff.avatar.url if interaction.user.avatar else None,
                            )
                        )
                    else:
                        await interaction.response.send_message(
                            embed=embeds.create_embed(
                                title="***Couldn't perform this action***",
                                description="`Invalid user to transfer to..`",
                            ),
                            ephemeral=True,
                        )
                else:
                    await interaction.response.send_message(
                        embed=embeds.NOT_CLMR, ephemeral=True
                    )
            else:
                await interaction.response.send_message(
                    "`Ticket doesn't exist in the json file anymore`",
                    ephemeral=True
                )

        else:
            await interaction.response.send_message(
                embed=embeds.MISSING_PERM, ephemeral=True
            )


class TransferView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TransferSelect())
