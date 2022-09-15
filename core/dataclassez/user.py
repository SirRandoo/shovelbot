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
import dataclasses
import typing

from PySide2 import QtGui

__all__ = ['User']


@dataclasses.dataclass()
class User:
    """The base class for platform users.  This class is responsible for
    defining the bare minimum all platforms are expected to provide."""
    username: str
    display_name: str
    color: typing.Optional[QtGui.QColor] = dataclasses.field(default_factory=QtGui.QColor)
    moderator: bool = dataclasses.field(default=False)
