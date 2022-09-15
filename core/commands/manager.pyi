# This file is part of ShovelBot.
#
# ShovelBot is free software:
# you can redistribute it
# and/or modify it under the
# terms of the GNU General
# Public License as published by
# the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later
# version.
#
# ShovelBot is distributed in
# the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without
# even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with
# ShovelBot.  If not,
# see <https://www.gnu.org/licenses/>.
import logging

from PyQt5 import QtCore
import typing

from .command import Command
from .group import Group
from .context import Context
from .abstract import Converter

any_command: typing.Union[Command, Group]


class ParseResult(typing.NamedTuple):
    command: any_command
    arguments: typing.List[str]


__all__ = ['Manager']


class Manager(QtCore.QObject):
    """A class for managing command input."""
    LOGGER: typing.ClassVar[logging.Logger]
    PARSER_DEBUG: typing.ClassVar[bool]
    
    onCommandExecuteRequested = QtCore.pyqtSignal[Context]
    """Emitted when a user invokes a command.  Listeners can emit
    `denyCommandExecute` when the context object passed through this signal to
    deny the command execution.  If no listener objects to the execution, the
    command's invocation will proceed."""
    
    onCommandExecute: QtCore.pyqtSignal[Context]
    """Emitted when a user invokes a command.  This signal is only emitted when
    no listeners to `onCommandExecuteRequested` objects to the command's
    execution."""
    
    denyCommandExecute = QtCore.pyqtSignal[Context]
    """When a command execution is requested, listeners to
    `onCommandExecuteRequested` are permitted to emit this signal to deny the
    command's execution.  The context object passed through
    `onCommandExecuteRequested` must be emitted through this signal, or the
    command's execution will proceed as usual."""
    
    commands: typing.List[any_command]
    converters: typing.List[Converter]
    
    def __init__(self, parent: QtCore.QObject = None):
        super(Manager, self).__init__()
    
    def parse(self, content: str, *, ignore_case: bool = None) -> ParseResult:
        """Parses a string `content` into a valid command.
        
        :raises CommandNotFound: The input given doesn't correspond to any
                                 registered command.
        """
    
    def convert_args(self, command: typing.Callable, *args, **kwargs) -> typing.Tuple[typing.Dict[object], typing.Dict[str]]:
        """Converts any arguments into the command's expected arguments.
        
        :returns: A tuple containing the transformed arguments, and the
                    untransformed, original arguments."""
    
    @staticmethod
    def is_kv_pair(content: str) -> bool:
        """Validates the input `content` passed to ensure it is a proper Python
        identifier."""
    
    def invoke(self, content: str, *, ignore_case: bool = None):
        """Invokes a command with the arguments passed."""
