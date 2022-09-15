"""
This file is part of ShovelBot.

ShovelBot is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

ShovelBot is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
ShovelBot.  If not, see <https://www.gnu.org/licenses/>.
"""
from .extension import Extension
from .message import Message
from .platform import Platform

__all__ = ['Modifier']


class Modifier(Extension):
    """A class for modifying messages emitted by Platforms.  This class should
    be used when you want to modify a message before it's displayed in the
    chat display."""

    # noinspection PyMethodMayBeStatic
    def should_modify(self, platform: Platform) -> bool:
        """Whether or not this modifier can modify messages for a platform.
        This is only used to dictate platform-specific modifications, such as
        Twitch emoticons."""
        return True

    # noinspection PyMethodMayBeStatic
    def modify(self, message: Message) -> Message:
        """Modifies a message from a platform."""
        return message
