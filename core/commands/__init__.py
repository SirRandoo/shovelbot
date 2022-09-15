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
from . import errors
from .command import Command
from .context import Context
from .group import Group
from .manager import Manager

__all__ = ['command', 'group', 'errors', 'Command', 'Group', 'Manager', 'Context']


def command(**kwargs):
    """A decorator for converting a callable into a Command instance."""

    def decorator(func):
        return Command(func=func, **kwargs)

    return decorator


def group(**kwargs):
    """A decorator for converting a callable into a Group instance."""

    def decorator(func):
        return Group(func=func, **kwargs)

    return decorator
