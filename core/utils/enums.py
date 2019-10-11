# This file is part of ShovelBot.
#
# ShovelBot is free software:
# you can redistribute it and/or
# modify it under the terms of the
# GNU General Public License as
# published by the Free Software
# Foundation, either version 3 of
# the License, or (at your option)
# any later version.
#
# ShovelBot is
# distributed in the hope that it
# will be useful, but WITHOUT ANY
# WARRANTY; without even the implied
# warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License
# for more details.
#
# You should have received a copy of
# the GNU General Public License along
# with ShovelBot.
# If not, see <http://www.gnu.org/licenses/>.
import enum

__all__ = ['BanBehaviors', 'DatabaseTypes', 'ExtensionStates']


class BanBehaviors(enum.Enum):
    """The different ways the bot will react when a user
    has been banned."""
    IGNORE_MESSAGES = 0
    HIDE_MESSAGES = 1
    REMOVE_MESSAGES = 2
    REMOVE_MESSAGE = 3


class DatabaseTypes(enum.Enum):
    """The different databases the bot supports."""
    SQLITE = 1
    MYSQL = 2
    POSTGRESQL = 3


class ExtensionStates(enum.Enum):
    """The different states an extension can be in."""
    UNLOADED = enum.auto()
    LOADED = enum.auto()
    
    SET_UP = enum.auto()
    TORN_DOWN = enum.auto()
    
    STARTED = enum.auto()
    HALTED = enum.auto()
    STOPPED = enum.auto()
