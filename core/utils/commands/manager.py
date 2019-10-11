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
import collections
import inspect
import logging
import sys
import typing

from PyQt5 import QtCore

from . import converters, errors
from .abstract import Converter
from .command import Command
from .group import Group

if typing.TYPE_CHECKING:
    any_command = typing.Union[Command, Group]

__all__ = ['Manager']


class Manager(QtCore.QObject):
    """Manages all commands.
    
    Any input will be parsed into valid command segments.  The segments are then
    passed to the requested command.  If the command was found, any arguments
    passed will be converted to their corresponding Python objects, then passed
    to the command as arguments."""
    LOGGER = logging.getLogger('utils.commands.manager')
    PARSER_DEBUG = '--debug-command-parser' in sys.argv
    
    # `onCommandExecuteRequested` is emitted when a user invokes a command.
    # Listeners can emit `denyCommandExecute` with the context object passed though
    # this signal to deny the command execution.  If no listener objects to the
    # execution, the command will be invoked as normal.
    onCommandExecuteRequested = QtCore.pyqtSignal(object)
    
    # `onCommandExecute` is emitted when a user invokes a command.
    # Before this signal is emitted, the user's requested command trigger
    # `onCommandExecuteRequested`.  Details on `onCommandExecuteRequested` can
    # be found in its comment block.
    #
    # Once no listeners object, the command will execute as normal, then this
    # signal will be emitted.  Attempting to emit `denyCommandExecute` when
    # this signal is emitted will do nothing.
    #
    # This signal emits with the context object created for the user's request.
    onCommandExecute = QtCore.pyqtSignal(object)
    
    # `denyCommandExecute` should be emitted when a listener to
    # `onCommandExecuteRequested` objects to the user's request to execute a
    # specific command.  The context object passed to listeners of
    # `onCommandExecuteRequested` should also be passed when emitting this
    # signal.
    denyCommandExecute = QtCore.pyqtSignal(object)
    
    def __init__(self, parent: QtCore.QObject = None):
        super(Manager, self).__init__(parent=parent)
        
        self.commands: typing.List['any_command'] = []
        self.converters: typing.List[Converter] = [
            inst for attr, inst in inspect.getmembers(converters)
            if inspect.isclass(inst) and any([c == Converter for c in inspect.getmro(inst)])
        ]
    
    def parse(self, content: str, *, ignore_case: bool = None) -> typing.Tuple['any_command', typing.List[str]]:
        """Parses a raw string into a valid command.  If the command was found,
        any segments remaining will be returned as-is."""
        if ignore_case is None:
            ignore_case = False
        
        segments: typing.List[str] = []
        quoted = False
        segment = ''
        
        # Parse the command string
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
        
        # Attempt to locate the invoked command
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
        
        return cmd, list(queue)
    
    def convert_args(self, command: typing.Callable, *args, **kwargs) -> \
            typing.Tuple[typing.Dict[str, object], typing.Dict[str, str]]:
        """Converts any arguments into the command's expected arguments."""
        argspec = inspect.getfullargspec(command)
        positionals = [a for a in argspec.args if a != 'self']
        arguments, originals = {}, {}
        
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
    def is_kv_pair(content: str) -> bool:
        """Returns whether or not the content passed could be a valid Python
        kwargs argument.  This does not check for the presence of a kwargs
        argument; that should be done by the invokee."""
        try:
            key, value = content.split('=')  # type: str, str
        
        except ValueError:
            return False
        
        else:
            return key[0].isalpha() or key[0] == '_'
    
    def invoke(self, content: str, *, ignore_case: bool = None):
        """Invokes a command, if found, with the arguments passed."""
        command, arguments = self.parse(content, ignore_case=ignore_case)
        
        if command is not None:
            argspec = inspect.getfullargspec(command.func)
            
            # Attempt to split the key-value arguments from the positional arguments
            key_arguments = {}
            
            for argument in arguments.copy():
                if '=' in argument and self.is_kv_pair(argument):
                    k, v = argument.split('=')
                    
                    # Assign the pair to the `key_arguments` dict to use later.
                    # If the value is an empty string, we'll forcibly assign
                    # the value to None.
                    key_arguments[k] = v if v else None
                    
                    # Ensure the key-value pairs are removed from the positional arguments
                    arguments.pop(arguments.index(argument))
            
            # Parse the arguments into the command's expected arguments
            args, originals = self.convert_args(command.func, *arguments, **key_arguments)
            
            # Since varargs isn't supported by `convert_args`, we'll comb through
            # the argument table to see if any weren't passed.
            #
            # If the command's callable has a varargs, we'll just plop
            if not argspec.varargs:
                final_positionals = []
                
                for key, value in originals.items():
                    if key not in args:
                        final_positionals.append(value)
            
            else:
                final_positionals = arguments
            
            command.func(*final_positionals, **args)
