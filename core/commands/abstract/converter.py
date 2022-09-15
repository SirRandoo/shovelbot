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
import abc
import typing

__all__ = ['Converter']


class Converter(abc.ABC):
    """Converters transform arguments into objects."""

    @classmethod
    @abc.abstractmethod
    def result(cls) -> typing.Any:
        """The final object class this converter will return should `convert`
        be invoked.  This method is used to ensure this converter is suited
        for the requested object."""

    @classmethod
    @abc.abstractmethod
    def convert(cls, argument: str) -> object:
        """Converts a raw argument to an object."""
