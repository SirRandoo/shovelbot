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
import enum

__all__ = ['BanBehaviors', 'DatabaseTypes', 'ExtensionStates']


class BanBehaviors(enum.IntFlag):
    IGNORE_MESSAGES = 0
    HIDE_MESSAGES = 2 | IGNORE_MESSAGES
    REMOVE_MESSAGES = 4 | IGNORE_MESSAGES | HIDE_MESSAGES
    REMOVE_MESSAGE = 8 | IGNORE_MESSAGES | HIDE_MESSAGES


class DatabaseTypes(enum.IntEnum):
    SQLITE = 1


class ExtensionStates(enum.Enum):
    UNLOADED = enum.auto()
    LOADED = enum.auto()

    SET_UP = enum.auto()
    TORN_DOWN = enum.auto()

    STARTED = enum.auto()
    HALTED = enum.auto()
    STOPPED = enum.auto()
