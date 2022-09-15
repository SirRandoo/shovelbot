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
import logging
import typing

from PyQt5 import QtNetwork, QtWidgets

from core.widgets import ShovelBot


__all__ = ['QApp']


@dataclasses.dataclass()
class QApp(QtWidgets.QApplication):
    """A custom application class for providing unified resources."""
    logger: typing.ClassVar[logging.Logger]
    
    client: ShovelBot
    network_access_manager: QtNetwork.QNetworkAccessManager
    
    debug_mode: bool
    disable_updater: bool
    redirect_policy: int
    
    args: dataclasses.InitVar[typing.List[str]]
    
    def __post_init__(self, args: typing.List[str]): ...
    
    def set_redirect_policy(self, value: int):
        """Sets the redirect policy for the application's network access
        manager."""
    
    def exec(self):
        """Enters the main event loop and waits until exit() is called.
        Returns the value that was passed to exit() (which is 0 if exit() is
        called via quit()).

        It is necessary to call this method to start event handling.  The main
        event loop receives events from the window system and dispatches these
        to the application widgets.

        To make your application perform idle processing (by executing a
        special function whenever there are no pending events), use a QTimer
        with 0 timeout.  More advanced idle processing schemes can be achieved
        using processEvents().

        Qt recommends that you connect clean-up code to the aboutToQuit()
        signal, instead of putting it in your application's main() method
        because on some platforms the exec() call may not return.  For example,
        on Windows when the user logs off, the system terminates the process
        after Qt closes all top-level windows.  Hence, there is no guarantee
        that the application will have time to exit its event loop and execute
        code at the end of the main() method after the exec() call."""
