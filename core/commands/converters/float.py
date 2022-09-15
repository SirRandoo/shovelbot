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

__all__ = ['FloatConverter']


class FloatConverter(Converter):
    """Converts a string into a float."""

    @classmethod
    def result(cls) -> typing.Type[float]:
        return float

    @classmethod
    def convert(cls, argument: str) -> float:
        try:
            return float(argument)

        except ValueError as e:
            raise errors.InvalidArgument from e
