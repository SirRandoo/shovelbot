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

import dataclasses
import typing

from PyQt5 import QtCore

from .extension import Extension
from .user import User

__all__ = ['Platform']


@dataclasses.dataclass()
class Platform(Extension):
    """Contains boilerplate code for platform extensions.
    
    *Platforms should only implement signals and methods that their platform can
    reliably support."""
    # `onMessage` should emit when a platform receives a new message.  The
    # signal should emit a message dataclass.
    onMessage: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object)
    
    # `onUserJoin` should emit when a platform detects a new user has joined
    # the channel.  The signal should emit a user dataclass.
    onUserJoin: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object)
    
    # `onUserLeave` should emit when a platform detects a user has left the
    # channel.  The signal should emit a user dataclass.
    onUserLeave: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object)
    
    # `onUserBanned` should emit when a platform detects a user has been
    # banned.  The signal should emit a user dataclass and a float.  The float
    # should be the duration of the ban, or `math.inf` if there is no duration.
    onUserBanned: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object, float)
    
    # `onUserUnbanned` should emit when a platform detects a user has been
    # unbanned.  The signal should emit a user dataclass.
    onUserUnbanned: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object)
    
    # `onUserPromoted` should emit when a platform detects a user has been
    # promoted.  "Promoted" is a generic term for a standard user becoming
    # a channel moderator. The signal should emit a user dataclass.
    onUserPromoted: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object)
    
    # `onUserDemoted` should emit when a platform detects a user has been
    # demoted.  "Demoted" is a generic term for a channel moderator becoming
    # a standard user.  The signal should emit a user dataclass.
    onUserDemoted: typing.ClassVar[QtCore.pyqtSignal] = QtCore.pyqtSignal(object)
    
    # Message methods
    def send_message(self, message: str):
        """Sends a message to the channel."""
    
    # Moderation methods
    def ban_user(self, user: User, duration: float):
        """Bans a user from the channel for `duration`.  If the duration is
        `math.inf`, this should be considered permanent, else it should be taken
        as is."""
    
    def unban_user(self, user: User):
        """Unbans a user from the channel."""
    
    # Privileges methods
    def promote_user(self, user: User):
        """Promotes a standard user to a moderator."""
    
    def demote_user(self, user: User):
        """Demotes a moderator to a standard user."""
