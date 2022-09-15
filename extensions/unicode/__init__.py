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
from PySide2 import QtCore

from core import dataclassez


class Unicode(dataclassez.Extension):
    """Provides unicode support to the chat panel."""
    VERSION = QtCore.QVersionNumber(1, 0, 0)
    AUTHORS = {'SirRandoo'}
    WEBSITE = QtCore.QUrl('https://github.com/sirrandoo/shovelbot-unicode')
    DOCUMENTATION = QtCore.QUrl('https://sirrandoo.github.io/projects/shovelbot-unicode')

    def __post_init__(self, parent: QtCore.QObject = None):
        super(Unicode, self).__post_init__(parent=parent)
