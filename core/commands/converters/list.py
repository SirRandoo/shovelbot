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
# see <https://www.gnu.org/licenses/>.
import typing

from .. import errors
from ..abstract import Converter

__all__ = ['ListConverter']


class ListConverter(Converter):
    """Converts a separated list of items into a list."""
    separators = ";,|"

    @classmethod
    def result(cls) -> typing.Type[list]:
        return list

    @classmethod
    def convert(cls, argument: str, children: typing.Any = None) -> list:
        # Declarations
        argument = argument.strip()
        segments = []
        cache = ""
        multi = False
        sep = False

        # Find segments
        for char in argument:
            if char in cls.separators:
                if cache:
                    segments.append(cache)
                    cache = ""

                multi = False
                sep = True

            elif char == " " and not multi and not sep:
                if cache:
                    segments.append(cache)

                break

            elif char == '"':
                if not multi:
                    multi = True

                else:
                    multi = False

            else:
                if char != " ":
                    sep = False

                cache += char

        # Clean up segments
        if cache not in segments:
            segments.append(cache)

        segments = [s.strip() for s in segments if s]

        # Parse segments
        if children is not None:
            results = []

            for segment in segments:
                for converter in Converter.__subclasses__():
                    converter: Converter

                    if converter.result() == children:
                        results.append(converter.convert(segment))

            if results:
                return results

            else:
                raise errors.InvalidArgument(f'Arguments of type {children.__name__} excepted!')

        else:
            return segments
