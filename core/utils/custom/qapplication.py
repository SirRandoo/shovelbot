# This file is part of ShovelBot.
#
# ShovelBot is free software:
# you can redistribute it and/or
# modify it under the terms of the
# GNU General Public License as
# published by the Free Software
# Foundation, either version 3 of
# the License, or (at your option)
# any later version.
#
# ShovelBot is
# distributed in the hope that it
# will be useful, but WITHOUT ANY
# WARRANTY; without even the implied
# warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License
# for more details.
#
# You should have received a copy of
# the GNU General Public License along
# with ShovelBot.
# If not, see <http://www.gnu.org/licenses/>.
import dataclasses
import logging
import typing

from PyQt5 import QtCore, QtGui, QtNetwork, QtWidgets

from widgets import ShovelBot

__all__ = ['QApplication']


@dataclasses.dataclass()
class QApplication(QtWidgets.QApplication):
    """A custom application class for providing unified resources."""
    # Class attributes
    logger: typing.ClassVar[logging.Logger] = logging.getLogger('core.app')
    
    # Instance attributes
    client: ShovelBot = dataclasses.field(init=False)
    network_access_manager: QtNetwork.QNetworkAccessManager = dataclasses.field(init=False)
    
    # User attributes
    debug_mode: bool = dataclasses.field(init=False)
    disable_updater: bool = dataclasses.field(init=False)
    redirect_policy: int = dataclasses.field(init=False)
    
    # Init variables
    args: dataclasses.InitVar[typing.List[str]]
    
    def __post_init__(self, args: typing.List[str]):
        super(QApplication, self).__init__(args)
        
        # Attribute assignment
        self.client = ShovelBot()
        self.network_access_manager = QtNetwork.QNetworkAccessManager()
        
        # Metadata assignment
        self.setApplicationName('shovelbot')
        self.setApplicationDisplayName('ShovelBot: Portable')
        self.setApplicationVersion('0.2.0')
        self.setWindowIcon(QtGui.QIcon(self.client.ASSETS.filePath('icon.png')))
        self.setOrganizationName('SirRandoo')
        self.setOrganizationDomain(self.client.REPOSITORY.toDisplayString())
    
    # Setters
    def set_redirect_policy(self, value: int):
        """Sets the redirect policy for the application's network access manager."""
        value: QtNetwork.QNetworkRequest.RedirectPolicy
        
        self.network_access_manager.setRedirectPolicy(value)
        self.redirect_policy = value
    
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
        self.setStyle('fusion')
        
        for w in self.allWidgets():
            self.aboutToQuit.connect(w.close)
        
        QtCore.QTimer.singleShot(1, self.client.setup)
        return super(QApplication, self).exec()
