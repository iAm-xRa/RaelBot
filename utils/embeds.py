# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import discord
from typing import Optional, List
from utils import timestmp as time_util
import logging
from utils.config import load_config

botconfig = load_config()
botlogger = logging.getLogger("bot")

DEFAULT_COLOUR = botconfig.default_embed_color
DEFAULT_FOOTER = botconfig.default_footer_text
DEFAULT_FOOTER_ICON = botconfig.default_footer_icon
DEFAULT_THMBNL = botconfig.default_embed_thumbnail


def create_embed(
    *,
    title: Optional[str] = None,
    description: Optional[str] = None,
    color: discord.Color | int = DEFAULT_COLOUR,
    footer: Optional[str] = DEFAULT_FOOTER,
    footer_ico: Optional[str] = DEFAULT_FOOTER_ICON,
    author: Optional[str] = None,
    author_url: Optional[str] = None,
    author_ico: Optional[str] = None,
    thumbnail: Optional[str] = DEFAULT_THMBNL,
    image: Optional[str] = None,
    fields: Optional[List[tuple]] = None,
    timestamp: bool = True,
    replace: bool = False,
    placeholders: Optional[tuple] = None,
) -> discord.Embed:
    """
    The utility for returing easily customizable discord.Embed objects.

    Fields Format:
    [("Field1 Name", "Field1 Value", inline : bool),
    ("Field2 Name", "Field2 Value", inline : bool)
    ]

    Placeholders Format is (Username, Displayname, Guildname)

    If replace is set to True, Placeholders will be replaced with the
    placeholders tuple's Values.
    """
    if placeholders and replace:
        embed_replacer = Replacer(
            placeholders[0], placeholders[1], placeholders[2]
        )

    embed = discord.Embed(
        title=(
            embed_replacer.replace_placeholders(string=title)
            if replace
            else title
        ),
        description=(
            embed_replacer.replace_placeholders(string=description)
            if replace
            else description
        ),
        color=int(color) if isinstance(color, int) else color,
    )

    if footer:
        if footer_ico:
            embed.set_footer(
                text=(
                    embed_replacer.replace_placeholders(string=footer)
                    if replace
                    else footer
                ),
                icon_url=footer_ico,
            )
        else:
            embed.set_footer(
                text=(
                    embed_replacer.replace_placeholders(string=footer)
                    if replace
                    else footer
                )
            )

    if author:
        if author_url and author_ico:
            embed.set_author(name=author, url=author_url, icon_url=author_ico)
        elif author_url:
            embed.set_author(name=author, url=author_url)
        elif author_ico:
            embed.set_author(name=author, icon_url=author_ico)
        else:
            embed.set_author(name=author)

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    if image:
        embed.set_image(url=image)

    if fields:
        if replace:
            for name, value, inline in fields:
                embed.add_field(
                    name=embed_replacer.replace_placeholders(string=name),
                    value=value,
                    inline=inline,
                )
        else:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

    if timestamp:
        embed.timestamp = time_util.discord_timestamp()

    return embed


async def update_ticket_embed_field(
    channel: discord.TextChannel,
    message_id: int,
    field_name: str,
    new_value: str,
):
    try:
        msg = await channel.fetch_message(message_id)
        embed = msg.embeds[0]
        fields = [(f.name, f.value, f.inline) for f in embed.fields]
        for i, (name, value, inline) in enumerate(fields):
            if name == field_name:
                fields[i] = (name, new_value, inline)
                break
        else:
            fields.append((field_name, new_value, True))

        new_embed = create_embed(
            title=embed.title, description=embed.description
        )
        if embed.thumbnail:
            new_embed.set_thumbnail(url=embed.thumbnail.url)
        if embed.image:
            new_embed.set_image(url=embed.image.url)
        if embed.footer:
            new_embed.set_footer(
                text=embed.footer.text,
                icon_url=embed.footer.icon_url
            )
        for name, value, inline in fields:
            new_embed.add_field(name=name, value=value, inline=inline)
        await msg.edit(embed=new_embed)
    except Exception as e:
        botlogger.warning(f"Failed to update embed field: {e}")


# Put the function in a class to make the usage in the rest of
# the code readable
class Replacer:
    "Replace placeholders with their values"

    def __init__(
        self,
        username: str = None,
        displayname: str = None,
        guildname: str = None,
    ):
        self.username = str(username)
        self.displayname = displayname
        self.guildname = guildname

    # This was made to make the bot config better..
    def replace_placeholders(self, string: str):
        placeholders = {
            "<member-username>": (
                self.username if self.username else "<member-username>"
            ),
            "<guild-name>": (
                self.guildname if self.guildname else "<guild-name>"
            ),
            "<member-displayname>": (
                self.displayname
                if self.displayname
                else "<member-displayname>"
            ),
        }

        for key, value in placeholders.items():
            if key != value:
                string = string.replace(key, value)

        return string


# Some useful embeds

PRFX_CMD_WARN = create_embed(
    title="***Command can't be executed !***",
    description=(
        "*I'm sorry but this command can't be used as a prefix "
        "command due to its complexity.*\n`But it's not over, "
        "instead use the slash command version of it !`"
    ),
    color=botconfig.default_embed_error_color,
)

MISSING_PERM = create_embed(
    title="***Missing Permission !***",
    description=(
        "*Hey ! you don't have permissions to execute this command,\n"
        " I will not allow you !*"
    ),
    color=botconfig.default_embed_error_color,
)

BAD_ARG = create_embed(
    title="***Bad Argument/s !***",
    description="`Make sure you have provided valid argument/s.`",
    color=botconfig.default_embed_error_color,
)

MISSING_ARG = create_embed(
    title="***Missing Argument/s !***",
    description="`Make sure you have provided the required argument/s.`",
    color=botconfig.default_embed_error_color,
)

EMBD_SCCS = create_embed(
    title="***Successfully Created Your Ticket***",
    description="*Thank you for using our service !*",
)

RATING_INVALID = create_embed(
    title="***You have entered an invalid rating.***",
    description="`Please make sure to provide a valid rating.`",
    color=botconfig.default_embed_error_color
)

TICK_PNLEMB = create_embed(
    title=botconfig.t_embed_title,
    description=botconfig.t_embed_description,
)

MISSING_SELECT = create_embed(
    title="***Missing Ticket Purpose !***",
    description=(
        "`Make sure you have selected the ticket purpose first "
        "before creating it !`"
    ),
    color=botconfig.default_embed_error_color,
)

UNEXPCTD_ERR = create_embed(
    title="***Unexpected Error !***",
    description=(
        "*Uh oh... it seems we have a serious problem here..*\n"
        "`You can contact my creator on his discord account for "
        "troubleshooting !`\n*His username is* `@nihlistoic` *!*"
    ),
    color=botconfig.default_embed_error_color,
)

NOT_TCKT = create_embed(
    title="***Couldn't perform action***",
    description="`This channel is not a ticket.`",
    color=botconfig.default_embed_error_color
)

CORD_FORBIDDEN = create_embed(
    title="***I do not have permissions to do this action***",
    description="`Please give me permissions in your server :(`",
    color=botconfig.default_embed_error_color
)

NOT_CLMR = create_embed(
    title="***Couldn't perform action***",
    description="`You are not the ticket claimer.`",
    color=botconfig.default_embed_error_color
)

NO_BOTS = create_embed(
    title="***Couldn't perform action***",
    description="`You can't add a bot.`",
    color=botconfig.default_embed_error_color
)

TCKT_LMT_USR = create_embed(
    title="***Ticket limit reached !***",
    description=(
        "`Sorry you have reached your ticket limit, you can't "
        "create a ticket until you close a/some ticket/s.`"
    ),
    color=botconfig.default_embed_error_color
)

TCKT_LMT_SRVR = create_embed(
    title="***Ticket limit reached !***",
    description=(
        f"`Sorry but there are currently more than "
        f"{botconfig.tickets_limit} tickets..\n"
        f"Please try creating a ticket later !`"
    ),
    color=botconfig.default_embed_error_color
)

REVIEW_EMBD = create_embed(
    title=botconfig.rvw_embed_title,
    description=botconfig.rvw_embed_description,
)

RESP_REVIEW = create_embed(
    title="***Your review has been submitted !***",
    description="`Thank you for using our services !`",
)

NO_SRVC = create_embed(
    title="***I think there's an issue here...***",
    description="`You never used our services, did you?`",
    color=botconfig.default_embed_error_color
)

WAITLISTED = create_embed(
    title="***Ticket is waitlisted***",
    description="`This ticket has been waitlisted due to inactivity.`",
)

CHANNEL_ERR = create_embed(
    title="***I couldn't create your ticket channel !***",
    description="`Please contact a mod or an admin !`",
    color=botconfig.default_embed_error_color
)

NO_SELF_REMOVE = create_embed(
    title="***You can't remove yourself !***",
    description="`Nice try :)`",
    color=botconfig.default_embed_error_color
)

ALREADY_BLACKLISTED = create_embed(
    title="***This member is already blacklisted!***",
    description="`To remove them from the blacklist use the remove_from_blacklist command!`",
    color=botconfig.default_embed_error_color
)

NO_BOT_BLACKLIST = create_embed(
    title="***You cannot blacklist a bot!***",
    description="`Next time try blacklisting a real discord member in your server!`",
    color=botconfig.default_embed_error_color
)

NO_SELF_BLACKLIST = create_embed(
    title="***You cannot blacklist Yourself!***",
    description="`Self hate is not a good thing, you know..`",
    color=botconfig.default_embed_error_color
)

NO_ADMIN_BLACKLIST = create_embed(
    title="***You cannot blacklist an admin!***",
    description="`Your fellow admins are good people..`",
    color=botconfig.default_embed_error_color
)

BOT_REMOVE_BLACKLIST = create_embed(
    title="***You cannot remove a bot from the blacklist!***",
    description="`They shouldn't be there anyways..`",
    color=botconfig.default_embed_error_color
)

BLACKLISTED = create_embed(
    title="***I think I have some bad news for you!***",
    description="`You are blacklisted by the server admins, you can't create tickets or submit reviews.`",
    footer="Maybe you can try to appeal in some way?",
    color=botconfig.default_embed_error_color
)

HELP = create_embed(
    title="RaelBot — Admin Commands Help",
    description=(
        "RaelBot is a ticket and review management bot.\n"
        "Below is a list of all administrator-only commands and their usage."
    ),
    fields=[
        (
            "/ping",
            "Check if the bot is online and view its current latency.",
            False
        ),
        (
            "/create_embed",
            "Create a custom embed and send it to a specified channel.\n"
            "Required: channel, title, description\n"
            "Optional: footer text",
            False
        ),
        (
            "/deploy_ticket_panel",
            "Deploy the ticket creation panel allowing users to open tickets.",
            False
        ),
        (
            "/deploy_review_panel",
            "Deploy the review panel allowing users to submit reviews.",
            False
        ),
        (
            "/add_to_blacklist <member>",
            "Blacklist a member from creating tickets and submitting reviews.",
            False
        ),
        (
            "/remove_from_blacklist <member>",
            "Remove a member from the blacklist and restore ticket and review access.",
            False
        ),
        (
            "/help",
            "Display this help menu.",
            False
        ),
        (
            "Permissions",
            "All commands listed above are restricted to administrators only.",
            False
        ),
    ],
    footer="RaelBot • Admin Help"
)