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


__all__ = ['CommandNotFound', 'CommandsError', 'ConverterError', 'InvalidArgument']


class CommandsError(Exception):
    """The base class for all command related exceptions."""


class CommandNotFound(CommandsError):
    """This is exception is raised when a command could not be found."""


class ConverterError(CommandsError):
    """The base class for all converter related exceptions."""


class InvalidArgument(ConverterError):
    """This exception is raised when a converter is in capable of converting
    an argument into a usable object."""
