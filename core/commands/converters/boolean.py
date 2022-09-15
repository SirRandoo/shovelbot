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
import typing

from .. import errors
from ..abstract import Converter

__all__ = ['BooleanConverter']


class BooleanConverter(Converter):
    """Converts a bool-type value into a Python object."""

    @classmethod
    def convert(cls, argument: str) -> bool:
        argument = argument.lower()

        if argument in ['yes', 'y', 'ok', 'okay', 'sure', '1', 'true', 'enabled']:
            return True

        elif argument in ['no', 'n', 'cancel', 'nah', '0', 'false', 'disables']:
            return False

        else:
            raise errors.InvalidArgument(f'Expected type {cls.result().__name__};  received {argument}')

    @classmethod
    def result(cls) -> typing.Type[bool]:
        return bool
