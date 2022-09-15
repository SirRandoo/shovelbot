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
import collections
import inspect
import logging
import typing
from collections import namedtuple

import sys
from PySide2 import QtCore

from . import converters, errors
from .abstract import Converter
from .group import Group

__all__ = ['Manager']

# noinspection PyTypeChecker
ParseResult = namedtuple('ParseResult', {'command', 'arguments'})


class Manager(QtCore.QObject):
    LOGGER = logging.getLogger('utils.commands.manager')
    PARSER_DEBUG = '--debug-command-parser' in sys.argv

    onCommandExecuteRequested = QtCore.Signal(object)
    onCommandExecute = QtCore.Signal(object)
    denyCommandExecute = QtCore.Signal(object)

    def __init__(self, parent = None):
        # noinspection PySuperArguments
        super(Manager, self).__init__(parent=parent)

        self.commands = []
        self.converters = [
            inst
            for attr, inst in inspect.getmembers(converters)
            if inspect.isclass(inst) and any([c == Converter for c in inspect.getmro(inst)])
        ]

    def parse(self, content, *, ignore_case = None):
        if ignore_case is None:
            ignore_case = False

        segments: typing.List[str] = []
        quoted = False
        segment = ''

        for c in content:
            if c == '"':
                if quoted:
                    quoted = False
                    segments.append(segment)
                    segment = ''

                else:
                    quoted = True

            elif c == ' ' and not quoted:
                if segment != '':
                    segments.append(segment)
                    segment = ''

            else:
                segment += c

        if segment:
            segments.append(segment)

        cmd = None
        queue = collections.deque(segments)

        while len(queue) > 0:
            query = queue.popleft()
            found = False

            if cmd is None:
                for command in self.commands:
                    checks = command.aliases.copy() + [command.name]

                    if (ignore_case and any([query.lower() == c for c in checks])) or any([query == c for c in checks]):
                        cmd = command
                        found = True

            elif isinstance(cmd, Group):
                for command in cmd.children:
                    checks = command.aliases.copy() + [command.name]

                    if (ignore_case and any([query.lower() == c for c in checks])) or any([query == c for c in checks]):
                        cmd = command
                        found = True

            if not found:
                queue.appendleft(query)
                break

        if cmd is None:
            raise errors.CommandNotFound

        return ParseResult(cmd, list(queue))

    def convert_args(self, command, *args, **kwargs):
        argspec = inspect.getfullargspec(command)
        positionals = [a for a in argspec.args if a != 'self']
        arguments = {}
        originals = {}

        for index, positional in enumerate(positionals):
            try:
                arg = args[index]

            except IndexError:
                raise errors.CommandsError(f'Insufficient positional arguments passed!  Expected argument #{index} '
                                           f'({positional});  received None.')

            else:
                try:
                    arg_type = argspec.annotations[positional]

                except KeyError:
                    arguments[positional] = arg

                else:
                    for conv in self.converters:
                        if arg_type == conv.result():
                            arguments[positional] = conv.convert(arg)

                originals[positional] = arg

        for k, v in kwargs.items():
            try:
                arg_type = argspec.annotations[k]

            except KeyError:
                arguments[k] = v

            else:
                for conv in self.converters:
                    if arg_type == conv.result():
                        arguments[k] = conv.convert(v)

        return arguments, originals

    @staticmethod
    def is_kv_pair(content):
        try:
            key: str
            key, _ = content.split('=')

        except ValueError:
            return False

        else:
            return key[0].isalpha() or key[0] == '_'

    def invoke(self, content, *, ignore_case = None):
        result = self.parse(content, ignore_case=ignore_case)

        argspec = inspect.getfullargspec(result.command)
        key_arguments = {}

        for a in result.arguments.copy():
            if '=' in a and self.is_kv_pair(a):
                k, v = a.split('=')
                key_arguments[k] = v if v else None

                result.arguments.pop(result.arguments.index(a))

        args, originals = self.convert_args(result.command.func, *result.arguments, **key_arguments)

        if not argspec.varargs:
            final_positionals = []

            for key, value in originals.items():
                if key not in args:
                    final_positionals.append(value)

        else:
            final_positionals = result.arguments

        result.command.func(*final_positionals, **args)
