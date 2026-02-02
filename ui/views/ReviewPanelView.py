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
from utils import cooldowns
from ui.modals.ReviewModal import ReviewModal

botconfig = config.load_config()


class ReviewPanelView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = cooldowns.Cooldown(botconfig.rvw_cooldown * 60) # From minutes to seconds

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
        user_id = interaction.user.id
        if self.cooldown.is_on_cooldown(user_id):
            await interaction.response.send_message(
                content=f"`You're on cooldown. Wait {self.cooldown.get_time_remaining(user_id):.1f}s before using this again.`",
                ephemeral=True
            )
            return
        self.cooldown.set_last_interaction(user_id)
        count_user = await tickets.get_any_tickets_count_for_user(
            user_id=user_id
        )
        if count_user > 0:
            await interaction.response.send_modal(ReviewModal())
        else:
            await interaction.response.send_message(
                embed=embeds.NO_SRVC, ephemeral=True
            )
