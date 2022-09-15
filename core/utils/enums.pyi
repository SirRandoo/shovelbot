# This file is part of ShovelBot.
#
# ShovelBot is free software:
# you can redistribute it
# and/or modify it under the
# terms of the GNU General
# Public License as published by
# the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later
# version.
#
# ShovelBot is distributed in
# the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without
# even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with
# ShovelBot.  If not,
# see <https://www.gnu.org/licenses/>.
import enum

__all__ = ['BanBehaviors', 'DatabaseTypes', 'ExtensionStates']


class BanBehaviors(enum.IntFlag):
    """The different ways the bot will react when a user has been banned."""
    IGNORE_MESSAGES: int
    """When a user is banned from the bot application, they'll simply have their
    messages ignored whenever they try to use the bot."""
    HIDE_MESSAGES: int
    """When a user is banned from the bot application, they'll have their
    previous messages removed from the chat display.  Do note that this simply
    removes the messages from the bot's chat, **not** issues a channel ban."""
    REMOVE_MESSAGES: int
    """When a user is banned from the bot application, they'll have their
    previous messages removed from the chat display, and their messages removed
    from the platform's channel."""
    REMOVE_MESSAGE: int
    """This is similar to `REMOVE_MESSAGES`, but the main difference is this
    only affects a single message instead of their chat history."""


class DatabaseTypes(enum.IntEnum):
    """The different database types the bot supports."""
    SQLITE = 1
    """The bot will use a SQLite database to store its data."""


class ExtensionStates(enum.Enum):
    """The different states an extension can be in."""
    UNLOADED: ExtensionStates
    LOADED: ExtensionStates
    
    SET_UP: ExtensionStates
    TORN_DOWN: ExtensionStates
    
    STARTED: ExtensionStates
    HALTED: ExtensionStates
    STOPPED: ExtensionStates
