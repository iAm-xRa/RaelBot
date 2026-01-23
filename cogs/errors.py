# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
from discord.ext import commands
from discord import app_commands
import traceback
import logging
from utils import embeds

botlogger = logging.getLogger("bot")


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if hasattr(ctx.command, "on_error"):
            return
        if isinstance(error, commands.MissingPermissions):
            await self.safe_send(
                ctx,
                f"`You lack the required permissions to run this command: {error.missing_permissions}`",
                embed=embeds.MISSING_PERM,
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await self.safe_send(
                ctx,
                f"`I lack the required permissions to run this command: {error.missing_permissions}`",
                embed=embeds.CORD_FORBIDDEN,
            )
        elif isinstance(error, commands.CommandOnCooldown):
            await self.safe_send(
                ctx,
                f"`This command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.`",
            )
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.safe_send(
                ctx,
                f"`Missing required argument: -{error.param.name}-`",
                embed=embeds.MISSING_ARG,
            )
        elif isinstance(error, commands.BadArgument):
            await self.safe_send(
                ctx,
                f"`Bad argument: {error}`",
                embed=embeds.BAD_ARG
            )
        elif isinstance(error, commands.CheckFailure):
            await self.safe_send(
                ctx,
                "`You lack the required permissions to run this command`",
                embed=embeds.MISSING_PERM,
            )
        elif isinstance(error, commands.CommandNotFound):
            pass
        else:
            tb = "".join(
                traceback.format_exception(
                    type(error),
                    error,
                    error.__traceback__
                )
            )
            botlogger.error(f"Unhandled command error in {ctx.command}:\n{tb}")
            await self.safe_send(
                ctx, "`An unexpected error occurred.`",
                embed=embeds.UNEXPCTD_ERR
            )

    async def safe_send(
        self,
        ctx: commands.Context,
        content: str = None,
        embed: discord.Embed = None
    ):
        try:
            if content and embed:
                await ctx.send(content=content, embed=embed, ephemeral=True)
            elif content:
                await ctx.send(content=content, ephemeral=True)
            elif embed:
                await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            botlogger.error(f"Failed to send error message: {e}")
            botlogger.error(content)


class AppCommandErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_app_command_error(
        self, interaction: discord.Interaction, error: app_commands.AppCommandError
    ):
        send_func = interaction.response.send_message
        if interaction.response.is_done():
            send_func = interaction.followup.send

        if isinstance(error, app_commands.MissingPermissions):
            await self.safe_send(
                send_func,
                "`You lack the required permissions to use this command.`",
                embed=embeds.MISSING_PERM,
            )
        elif isinstance(error, app_commands.BotMissingPermissions):
            await self.safe_send(
                send_func,
                "`I lack the required permissions to run this command.`",
                embed=embeds.CORD_FORBIDDEN,
            )
        elif isinstance(error, app_commands.CommandOnCooldown):
            await self.safe_send(
                send_func,
                f"`This command is on cooldown. Try again in {round(error.retry_after, 1)} seconds.`",
            )
        elif isinstance(error, app_commands.CheckFailure):
            await self.safe_send(
                send_func,
                "`You lack the required permissions to run this command`",
                embed=embeds.MISSING_PERM,
            )
        elif isinstance(error, app_commands.TransformerError):
            await self.safe_send(
                send_func, f"`Invalid argument: {error}`", embed=embeds.BAD_ARG
            )
        elif isinstance(error, app_commands.CommandInvokeError):
            tb = "".join(
                traceback.format_exception(
                    type(error.original),
                    error.original,
                    error.original.__traceback__
                )
            )
            botlogger.error(
                f"Slash command invoke error in {interaction.command}:\n{tb}"
            )
            await self.safe_send(
                send_func,
                "`An unexpected error occurred while executing this command.`",
                embed=embeds.UNEXPCTD_ERR,
            )
        else:
            tb = "".join(
                traceback.format_exception(
                    type(error),
                    error,
                    error.__traceback__
                )
            )
            botlogger.error(
                f"Unhandled slash command error in {interaction.command}:\n{tb}"
            )
            await self.safe_send(
                send_func, "`An unexpected error occurred.`",
                embed=embeds.UNEXPCTD_ERR
            )

    async def safe_send(
        self, send_func, content: str = None, embed: discord.Embed = None
    ):
        try:
            if content and embed:
                await send_func(content=content, embed=embed, ephemeral=True)
            elif content:
                await send_func(content=content, ephemeral=True)
            elif embed:
                await send_func(embed=embed, ephemeral=True)
        except Exception as e:
            botlogger.error(f"Failed to send app command error message: {e}")
            botlogger.error(content)


class ViewModalErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_error(self, event_method: str, *args, **kwargs):
        error = kwargs.get("error")
        if not error:
            return
        tb = "".join(
            traceback.format_exception(type(error), error, error.__traceback__)
        )
        botlogger.error(
            f"Unhandled error in View/Modal event {event_method}:\n{tb}"
        )
        target_interaction: discord.Interaction | None = None

        if args:
            first_arg = args[0]
            if isinstance(first_arg, discord.Interaction):
                target_interaction = first_arg

        if target_interaction:
            await self.safe_send(
                target_interaction,
                content="`An unexpected error occurred.`",
                embed=embeds.UNEXPCTD_ERR,
            )

    async def safe_send(
        self,
        interaction: discord.Interaction,
        content: str = None,
        embed: discord.Embed = None,
    ):
        try:
            send_func = interaction.response.send_message
            if interaction.response.is_done():
                send_func = interaction.followup.send

            if content and embed:
                await send_func(content=content, embed=embed, ephemeral=True)
            elif content:
                await send_func(content=content, ephemeral=True)
            elif embed:
                await send_func(embed=embed, ephemeral=True)
        except Exception as e:
            botlogger.error(f"Failed to send View/Modal error message: {e}")
            botlogger.error(content)


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))
    await bot.add_cog(AppCommandErrorHandler(bot))
    await bot.add_cog(ViewModalErrorHandler(bot))
