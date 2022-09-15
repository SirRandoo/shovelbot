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

from PySide2 import QtCore, QtWidgets, QtSql
import commands
from core import dataclassez

if typing.TYPE_CHECKING:
    from core.utils import custom


__all__ = ['Quotes']


class Quotes(dataclassez.Extension):
    """The core of the Quotes extension."""
    # Signals
    QUOTE_ADDED = QtCore.Signal(object)  # Quote instance
    QUOTE_REMOVED = QtCore.Signal(object)  # Quote instance
    QUOTE_CHANGED = QtCore.Signal(object, object)  # Quote instances

    # Class attributes
    DISPLAY_NAME = 'Quotes'
    VERSION = QtCore.QVersionNumber(1, 0, 0)
    AUTHORS = {'SirRandoo'}
    WEBSITE = QtCore.QUrl('https://github.com/sirrandoo/shovelbot-extensions')
    DOCUMENTATION = QtCore.QUrl('https://sirrandoo.github.io/projects/shovelbot-extensions/quotes')

    def __post_init__(self, parent: QtCore.QObject = None):
        # Super Call #
        super(Quotes, self).__post_init__(parent=parent)

        # Public attributes
        self.database = QtSql.QSqlDatabase.addDatabase('QSQLITE')

    # Commands
    @commands.group(
        name='quotes',
        description='The root command for quotes.',
        aliases=['quote']
    )
    def quotes(self):
        raise NotImplementedError
