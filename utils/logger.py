# RaelBot - Discord bot for ticket systems
# Copyright (C) 2026 iAm-xRa
#
# This file is part of RaelBot, a free software project.
# RaelBot is licensed under the GNU General Public License v3.
# You should have received a copy of the GPL along with this file.
# If not, see https://www.gnu.org/licenses/gpl-3.0.txt


import logging
import os


def setup_logger():
    os.makedirs("logs", exist_ok=True)

    botlogger = logging.getLogger("bot")
    botlogger.setLevel(logging.DEBUG)

    cnsl_hndlr = logging.StreamHandler()
    cnsl_hndlr.setLevel(logging.DEBUG)

    file_hndlr = logging.FileHandler("logs/bot.log", "a", "utf-8")
    file_hndlr.setLevel(logging.DEBUG)

    frmtr = logging.Formatter(
        "{asctime} : {levelname} : {message}", "%y / %m / %d : %H:%M", "{"
    )

    cnsl_hndlr.setFormatter(frmtr)
    file_hndlr.setFormatter(frmtr)

    botlogger.addHandler(cnsl_hndlr)
    botlogger.addHandler(file_hndlr)

    return botlogger
