# SPDX-FileCopyrightText: 2023-present Massimiliano Pippi <mpippi@gmail.com>
#
# SPDX-License-Identifier: MIT
from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: str
    content: str
