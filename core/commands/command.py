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

from . import errors

if typing.TYPE_CHECKING:
    from .group import Group

__all__ = ['Command']


class Command:
    """Represents a command in the command framework."""

    def __init__(self, **kwargs):
        self.name: str = kwargs.pop('name')
        self.func: callable = kwargs.pop('func')
        self.help: str = kwargs.get('help')
        self.usage: str = kwargs.get('usage')
        self.aliases: typing.List[str] = kwargs.get('aliases', [])
        self.enabled: bool = kwargs.get('enabled', True)
        self.description: str = kwargs.get('description')
        self.parent: typing.Union['Group'] = kwargs.get('parent', None)

    @property
    def qualified_name(self):
        return f'{self.parent.qualified_name} {self.name}' if self.parent is not None else self.name

    # Magic Methods #
    def __call__(self, *args, **kwargs):
        if self.func is not None:
            self.func(*args, **kwargs)

        else:
            raise errors.CommandsError("No callable specified!")

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.qualified_name} description={self.description}>"
