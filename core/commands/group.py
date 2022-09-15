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

from .command import Command


class Group(Command):
    """Represents a group of commands."""

    def __init__(self, **kwargs):
        super(Group, self).__init__(**kwargs)

        self.children: typing.List[Command, Group] = list()

    def command(self, **kwargs):
        """A decorator for converting a callable into a Command instance with
        this group as its parent."""

        def decorator(func):
            c = Command(func=func, parent=self, **kwargs)
            self.children.append(c)

            return c

        return decorator

    def group(self, **kwargs):
        """A decorator for converting a callable into a Group instance with this
        group as its parent."""

        def decorator(func):
            g = Group(func=func, parent=self, **kwargs)
            self.children.append(g)

            return g

        return decorator
