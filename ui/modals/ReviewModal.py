# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
from utils import config, embeds
import logging
import re

botconfig = config.load_config()
botlogger = logging.getLogger("bot")
rating_regex = r"^(?:10|[1-9])\s*(?:\/\s*10)?$"


class ReviewModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title=botconfig.rvw_modal_title)
        self.product = discord.ui.TextInput(
            label=botconfig.rvw_modal_label1,
            max_length=30,
            placeholder=botconfig.rvw_modal_place_holder1,
        )

        self.rating = discord.ui.TextInput(
            label="Rate our service out of 10 !",
            placeholder="Your rating goes here..",
            max_length=10,
        )

        self.comment = discord.ui.TextInput(
            label="You can write your comments here !",
            style=discord.TextStyle.paragraph,
            placeholder="Your comments go here..",
            min_length=24,
            max_length=300,
        )

        self.add_item(self.product)
        self.add_item(self.rating)
        self.add_item(self.comment)

    async def on_submit(self, interaction: discord.Interaction):
        if not re.fullmatch(rating_regex, self.rating.value.strip()):
            await interaction.response.send_message(
                embed=embeds.RATING_INVALID, ephemeral=True
            )
            return

        rating_match = re.match(r"^(10|[1-9])", self.rating.value.strip())
        rating_value = int(rating_match.group(1))
        channel = interaction.guild.get_channel(botconfig.reviews_channel)

        if not channel:
            try:
                channel = await interaction.guild.fetch_channel(
                    botconfig.reviews_channel
                )
            except (
                discord.NotFound,
                discord.Forbidden,
                discord.HTTPException,
            ) as e:
                botlogger.error(
                    f"The reviews channel could not be found.\n{e}"
                )
                await interaction.response.send_message(
                    (
                        (
                            "`Could not submit your review."
                            "Please contact a staff "
                            "member.`"
                        )
                    ),
                    ephemeral=True,
                )
                return
        await interaction.response.defer(ephemeral=True)
        review_embed = embeds.create_embed(
            title=(
                f"***New Review submitted by "
                f"{interaction.user.display_name} !***"
            ),
            fields=[
                (
                    f"{botconfig.rvw_embed_field1}",
                    f"`{self.product.value.strip()}`",
                    True,
                ),
                ("`Rating`", f"`{rating_value}/10`", True),
                ("`Comments`", f"`{self.comment.value.strip()}`", False),
            ],
            thumbnail=(
                interaction.user.avatar.url
                if interaction.user.avatar else None
            ),
            color=config.Config.parse_color("c10030"),
        )
        try:
            await channel.send(
                embed=review_embed,
                content=f"Submitted by {interaction.user.mention}",
            )
        except (discord.Forbidden, discord.HTTPException) as e:
            botlogger.error(
                f"Failed to send {interaction.user.name}'s review embed: {e}"
            )
            await interaction.followup.send(
                (
                    "`Could not submit your review. Please contact a staff "
                    "member.`"
                ),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            embed=embeds.RESP_REVIEW, ephemeral=True
        )
        botlogger.info(f"Review submitted by {interaction.user}.")
