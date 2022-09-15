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

from PySide2 import QtCore

from .extension import Extension
from .user import User

__all__ = ['Platform']


@dataclasses.dataclass()
class Platform(Extension):
    """Contains boilerplate code for platform extensions.

    *Platforms should only implement signals and methods that their platform can
    reliably support."""
    onMessage: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    """Emitted when a platform detects a new message. The emitted object should
    be an instance of the Message dataclass."""

    onUserJoin: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    """Emitted when a platform detects a user has joined the channel. The
    emitted object should be an instance of the User dataclass."""

    onUserLeave: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    """Emitted when a platform detects a user has left the channel. The emitted
    object should be an instance of the User dataclass."""

    onUserBanned: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object, float)
    """Emitted when a platform detects a user has been banned. The emitted
    object should be an instance of the User dataclass. If the ban is temporary,
    the platform should emit a float of the duration (in seconds). If the ban is
    permanent, the platform can emit `math.inf` or `-1`."""

    onUserUnbanned: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    """Emitted when a platform detects a user has been unbanned. The emitted
    object should be an instance of the User dataclass."""

    onUserPromoted: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    """Emitted when a platform detects a user has been promoted. The term
    "promoted" is an umbrella term for a user ranking up in the channel. The
    emitted object should be an instance of the User dataclass."""

    onUserDemoted: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    """Emitted when a platform detects a user has been demoted. The term
    "demoted" is an umbrella term for a user ranking down in the channel. The
    emitted object should be an instance of the User dataclass."""

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
