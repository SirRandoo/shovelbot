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
from .group import Group
from core import dataclassez

__all__ = ['Context']


class Context:
    def __init__(self, **kwargs):
        self.prefix: str = kwargs.pop('prefix')
        self.message: dataclassez.Message = kwargs.pop('message')
        self.platform: dataclassez.Platform = kwargs.pop('platform')
        self.command: typing.Union[Command, Group] = kwargs.pop('command')

        self.arguments: typing.List[str] = kwargs.get('arguments', [])
        self.kwarguments: typing.Dict[str, str] = kwargs.get('kwarguments', {})

    @property
    def invoker(self) -> dataclassez.User:
        return self.message.user
