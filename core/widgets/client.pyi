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
import typing

from PyQt5 import QtCore, QtWidgets, QtGui, QtHelp, QtSql

from core import commands, dataclassez
from .uis import Client as ClientUi
from .help import Help

from QtUtilities import requests, settings

__all__ = ['Client']


class Client(QtWidgets.QMainWindow):
    """An open source, modular bot to help streamers interact with their audience."""
    LOGGER: typing.ClassVar[logging.Logger]
    """The base logger for the client.  Any logger that branches off of 'core'
    will be outputted to the bot's main log file.  All other loggers should
    manually add handlers."""
    
    REPOSITORY: typing.ClassVar[QtCore.QUrl]
    """The location on the web of the source for this edition of the bot.  By
    default this points to https://github.com/sirrandoo/shovelbot"""
    
    RESOURCES: typing.ClassVar[QtCore.QDir]
    """The directory where the bot's resource files are stored."""
    
    ASSETS: typing.ClassVar[QtCore.QDir]
    """The directory where the bot's assets are stored.  Assets are typically
    icons, whereas resources have no typical filter."""
    
    AUTHORS: typing.ClassVar[typing.Set[str]]
    """The author(s) that are responsible for this edition of the bot.  Should
    an unofficial edition be made, SirRandoo should be removed from this set."""
    
    LICENSE: typing.ClassVar[str]
    """The license string for this edition.  This should typically by GPLv3+."""
    
    LICENSE_URL: typing.ClassVar[QtCore.QUrl]
    """The location on the web where users can read about the license."""
    
    aboutToStart: QtCore.pyqtSignal
    """Emitted when the bot is about to run its start code."""
    
    aboutToHalt: QtCore.pyqtSignal
    """Emitted when the bot is about to run its halt code."""
    
    aboutToStop: QtCore.pyqtSignal
    """Emitted when the bot is about to run its stop code."""
    
    started: QtCore.pyqtSignal
    """Emitted when the bot has finished running its start code."""
    
    halted: QtCore.pyqtSignal
    """Emitted when the bot has finished running its halt code."""
    
    stopped: QtCore.pyqtSignal
    """Emitted when the bot has finished running its stop code."""
    
    onCommandExecuteRequested = QtCore.pyqtSignal[commands.Context]
    """Emitted when a user invokes a command.  Listeners can emit
    `denyCommandExecute` when the context object passed through this signal to
    deny the command execution.  If no listener objects to the execution, the
    command's invocation will proceed."""
    
    onCommandExecute: QtCore.pyqtSignal[commands.Context]
    """Emitted when a user invokes a command.  This signal is only emitted when
    no listeners to `onCommandExecuteRequested` objects to the command's
    execution."""
    
    denyCommandExecute = QtCore.pyqtSignal[commands.Context]
    """When a command execution is requested, listeners to
    `onCommandExecuteRequested` are permitted to emit this signal to deny the
    command's execution.  The context object passed through
    `onCommandExecuteRequested` must be emitted through this signal, or the
    command's execution will proceed as usual."""
    
    ui: ClientUi
    help_dialog: typing.Optional[Help]
    request_factory: typing.Optional[requests.Factory]
    extensions: typing.Dict[str, typing.Union[dataclassez.ExtensionStub, dataclassez.Extension]]
    settings: settings.Display
    themes: typing.List[typing.Callable[[QtWidgets.QWidget], None]]
    display_timer: QtCore.QTimer
    base_theme: QtGui.QPalette
    help_engine: QtHelp.QHelpEngine
    command_manager: commands.Manager
    database: QtSql.QSqlDatabase
    
    _settings_file: typing.Optional[QtCore.QFile]
