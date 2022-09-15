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
import logging
import typing

from PySide2 import QtCore, QtGui, QtNetwork, QtWidgets

from widgets import Client

__all__ = ['QApp']


@dataclasses.dataclass()
class QApp(QtWidgets.QApplication):
    logger: typing.ClassVar[logging.Logger] = logging.getLogger('core.app')

    client: Client = dataclasses.field(init=False)
    network_access_manager: QtNetwork.QNetworkAccessManager = dataclasses.field(init=False)

    debug_mode: bool = dataclasses.field(init=False)
    disable_updater: bool = dataclasses.field(init=False)
    redirect_policy: int = dataclasses.field(init=False)

    args: dataclasses.InitVar[typing.List[str]]

    def __post_init__(self, args: typing.List[str]):
        # noinspection PySuperArguments
        super(QApp, self).__init__(args)

        self.client = Client()
        self.network_access_manager = QtNetwork.QNetworkAccessManager()

        self.setApplicationName('shovelbot')
        self.setApplicationDisplayName('ShovelBot: Portable')
        self.setApplicationVersion('0.2.0')
        self.setWindowIcon(QtGui.QIcon(self.client.ASSETS.filePath('icon.png')))
        self.setOrganizationName('SirRandoo')
        self.setOrganizationDomain(self.client.REPOSITORY.toDisplayString())

    def set_redirect_policy(self, value: QtNetwork.QNetworkRequest.RedirectPolicy):
        self.network_access_manager.setRedirectPolicy(value)
        self.redirect_policy = value

    def exec(self):
        self.setStyle('fusion')

        for w in self.allWidgets():
            self.aboutToQuit.connect(w.close)

        QtCore.QTimer.singleShot(1, self.client.setup)
        # noinspection PySuperArguments
        return super(QApp, self).exec()
