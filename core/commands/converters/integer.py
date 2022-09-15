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

__all__ = ['IntConverter']


class IntConverter(Converter):
    """Converts a string into an integer."""

    @classmethod
    def result(cls) -> typing.Type[int]:
        return int

    @classmethod
    def convert(cls, argument: str) -> int:
        try:
            return int(argument)

        except ValueError as e:
            raise errors.InvalidArgument from e
