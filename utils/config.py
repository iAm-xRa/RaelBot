# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


from pathlib import Path
import json

CONFIG_PATH = Path("config.json")


class Config:
    def __init__(self, data: dict):
        self._data = data

        self._bot_data: dict = data["bot"]
        self.guild_id: int = int(self._bot_data["guild_id"])
        self.prefix: str = v if (v := self._bot_data.get("prefix")) else "+"
        status: dict = self._bot_data.get("status", {})
        self.bot_activity: str = status.get("activity", "Powered by RaelBot")
        self.bot_activity_type: str = (
            status.get("type", "online")
            if status.get("type")
            in {"idle",
                "online",
                "offline",
                "dnd",
                "do_not_disturb",
                "invisible"
                }
            else "online"
        )

        self._roles_data: dict = data["roles"]
        self.admin_role_id: int = int(self._roles_data["admin_role_id"])
        self.support_role_id: int = int(self._roles_data["support_role_id"])
        self.member_role_id: int = (
            int(v) if (v := self._roles_data.get("member_role_id")) else None
        )

        self._tickets_data: dict = data["tickets"]
        self.first_purpose: str = self._tickets_data["purpose1"]
        self.second_purpose: str = self._tickets_data["purpose2"]
        self.active_tickets_category: int = int(
            self._tickets_data["active_tickets_category_id"]
        )
        self.inactive_tickets_category: int = int(
            self._tickets_data["inactive_tickets_category_id"]
        )
        self.max_user_tickets: int = int(
            self._tickets_data["max_open_by_user"]
        )
        self.inactive_after: int = int(self._tickets_data["inactive_after"])
        self.inactivity_loop_interval: int = int(
            self._tickets_data["inactivity_loop_interval_minutes"]
        )
        self.tickets_limit: int = int(
            self._tickets_data["total_tickets_limit"]
        )
        self.transcript_channel: int = int(
            self._tickets_data["transcripts_channel_id"]
        )
        self.reviews_channel: int = int(
            self._tickets_data["reviews_channel_id"]
        )

        self._ticket_panel_data: dict = data["ticket_panel"]
        self.t_embed_title: str = self._ticket_panel_data["title"]
        self.t_embed_description: str = self._ticket_panel_data["description"]
        self.t_label1: str = self._ticket_panel_data["purpose1_label"]
        self.t_label2: str = self._ticket_panel_data["purpose2_label"]
        self.t_description1: str = (
            self._ticket_panel_data["purpose1_description"]
        )
        self.t_description2: str = (
            self._ticket_panel_data["purpose2_description"]
        )
        self.t_placeholder: str = self._ticket_panel_data["placeholder"]

        self._rvw_panel_data: dict = data["review_panel"]
        self.rvw_embed_title: str = self._rvw_panel_data["title"]
        self.rvw_embed_description: str = self._rvw_panel_data["description"]
        self.rvw_cooldown = int(data["reviews_cooldown_per_user_in_minutes"])

        self._first_purpose_embed: dict = data["purpose1_embeds"]
        self.purpose1_embed_description: str = (
            self._first_purpose_embed["description"]
        )
        self.purpose1_embed_image: str = (
            self._first_purpose_embed["image_link"]
        )
        self.purpose1_field1: str = self._first_purpose_embed[
            "first_input_value_field_name"
        ]
        self.purpose1_field2: str = self._first_purpose_embed[
            "second_input_value_field_name"
        ]

        self._second_purpose_embed: dict = data["purpose2_embeds"]
        self.purpose2_embed_description: str = (
            self._second_purpose_embed["description"]
        )
        self.purpose2_embed_image: str = (
            self._second_purpose_embed["image_link"]
        )

        self.embed_data: dict = data["embeds"]
        self.default_embed_color = Config.parse_color(
            self.embed_data["default_color"]
        )
        self.default_embed_error_color = Config.parse_color(
            self.embed_data["default_error_color"]
        )

        self.default_footer_text: str = self.embed_data["default_footer_text"]
        self.default_footer_icon: str = (
            self.embed_data["default_footer_icon_link"]
        )
        self.default_embed_thumbnail: str = (
            self.embed_data["default_thumbnail_link"]
        )

        self._welcome_data: dict = data.get("welcome", {})
        self.welcome_channel: int = (
            int(v)
            if (v := self._welcome_data.get("welcome_channel_id"))
            else None
        )

        if self.welcome_channel:
            self.welcome_title: str = (
                self._welcome_data["welcome_embed_title"]
            )
            self.welcome_content: str = (
                self._welcome_data["welcome_embed_content"]
            )
            self.welcome_color = Config.parse_color(
                self._welcome_data["welcome_embed_color"]
            )
            self.welcome_image: str = (
                self._welcome_data["welcome_embed_image_link"]
            )

        self._ticket_modal_data: dict = data["ticket_create_modal"]
        self.ticket_modal_title: str = self._ticket_modal_data["title"]
        self.ticket_modal_label1: str = (
            self._ticket_modal_data["first_input_label"]
        )
        self.ticket_modal_place_holder1: str = self._ticket_modal_data[
            "first_input_placeholder"
        ]
        self.ticket_modal_label2: str = (
            self._ticket_modal_data["second_input_label"]
        )

        self._rvw_modal_data: dict = data["review_modal"]
        self.rvw_modal_title: str = self._rvw_modal_data["title"]
        self.rvw_modal_label1: str = self._rvw_modal_data["first_input_label"]
        self.rvw_modal_place_holder1: str = self._rvw_modal_data[
            "first_input_placeholder"
        ]

        self._rvw_embed_data = data["review_embed"]
        self.rvw_embed_field1: str = self._rvw_embed_data["field1"]

    @staticmethod
    def parse_color(color: int | str) -> int:
        """Hex code only."""
        if isinstance(color, int):
            return color

        color = str(color).strip().lower().replace("#", "").replace("0x", "")

        return int(color, 16)


def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"{CONFIG_PATH} is not found")
    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        data = json.load(config_file)

    return Config(data)
