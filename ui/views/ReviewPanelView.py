# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
from discord.ext import commands
from utils import tickets
from utils import config
from utils import embeds
from ui.modals.ReviewModal import ReviewModal

botconfig = config.load_config()


class ReviewPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(
            1, botconfig.rvw_cooldown * 60, commands.BucketType.default
        )

    @discord.ui.button(
        label="Submit Review",
        style=discord.ButtonStyle.blurple,
        custom_id="review:button",
    )
    async def review_btn(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        if await tickets.is_blacklisted(interaction.user.id):
            await interaction.response.send_message(embed=embeds.BLACKLISTED, ephemeral=True)
            return

        key = (
            interaction.guild.id if interaction.guild else None,
            interaction.user.id
        )
        bucket = self.cooldown.get_bucket(key)
        retry_after = bucket.update_rate_limit()

        if retry_after:
            await interaction.response.send_message(
                f"`You're on cooldown. Wait {retry_after:.1f}s before using this command again.`",
                ephemeral=True,
            )
            return

        user_id = interaction.user.id
        count_user = await tickets.get_any_tickets_count_for_user(
            user_id=user_id
        )
        if count_user > 0:
            await interaction.response.send_modal(ReviewModal())
        else:
            await interaction.response.send_message(
                embed=embeds.NO_SRVC, ephemeral=True
            )
