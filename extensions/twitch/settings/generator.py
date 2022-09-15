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
import logging
import secrets
import typing
from urllib import parse

from PySide2 import QtCore, QtWebEngineWidgets, QtWidgets

from ..dataclasses import token
from ..enums import Scopes

__all__ = ['Generator']


class Generator(QtWidgets.QDialog):
    """A dialog for generating a new Twitch token with the user's
    specified scopes."""
    LOGGER = logging.getLogger('extensions.twitch.token')

    # Signals
    GENERATED = QtCore.Signal(object)  # token.Token

    # Class attributes
    ENDPOINT = QtCore.QUrl('https://id.twitch.tv/oauth2/authorize')

    def __init__(self, *, parent: QtWidgets.QWidget = None):
        # Super call
        super(Generator, self).__init__(parent=parent)

        # Ui attributes
        # Top-level widgets
        self.stacked: typing.Optional[QtWidgets.QStackedWidget] = None

        # Stacked widgets
        self.browser_container: typing.Optional[QtWidgets.QWidget] = None
        self.scope_container: typing.Optional[QtWidgets.QWidget] = None

        # Browser widgets
        self.label: typing.Optional[QtWidgets.QLabel] = None
        self.browser: typing.Optional[QtWebEngineWidgets.QWebEngineView] = None

        # Scope widgets
        self.scopes: typing.Optional[QtWidgets.QListWidget] = None
        self.generate: typing.Optional[QtWidgets.QPushButton] = None

        # Private attributes
        self._state: typing.Optional[str] = None

    # Ui methods
    def setup_ui(self):
        """Sets up the generator's UI."""
        # Widget validation
        # Top-level
        if self.stacked is None:
            self.stacked = QtWidgets.QStackedWidget()

        # Stacks
        if self.browser_container is None:
            self.browser_container = QtWidgets.QWidget()

        if self.scope_container is None:
            self.scope_container = QtWidgets.QWidget()

        # Browser widgets
        if self.browser is None:
            self.browser = QtWebEngineWidgets.QWebEngineView()
            self.browser.urlChanged.connect(self.url_watcher)

        if self.label is None:
            self.label = QtWidgets.QLabel()
            self.label.setWordWrap(True)

        # Scope widgets
        if self.scopes is None:
            self.scopes = QtWidgets.QListWidget()

            for scope in Scopes.__members__.values():  # type: Scopes
                i = QtWidgets.QListWidgetItem(scope.value)
                i.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled)
                i.setCheckState(QtCore.Qt.Unchecked)

                self.scopes.addItem(i)

        if self.generate is None:
            self.generate = QtWidgets.QPushButton('Generate token')

            self.generate.clicked.connect(self.initiate)

        # Layout validation
        layout: QtWidgets.QGridLayout = self.layout()
        scope_layout: QtWidgets.QVBoxLayout = self.scope_container.layout()
        browser_layout: QtWidgets.QVBoxLayout = self.browser_container.layout()

        if layout is None:
            layout = QtWidgets.QGridLayout(self)

        if scope_layout is None:
            scope_layout = QtWidgets.QVBoxLayout(self.scope_container)
            scope_layout.setContentsMargins(0, 0, 0, 0)

        if browser_layout is None:
            browser_layout = QtWidgets.QVBoxLayout(self.browser_container)
            browser_layout.setContentsMargins(0, 0, 0, 0)

        # Generator layout
        if layout.indexOf(self.stacked) == -1:
            layout.addWidget(self.stacked)

        # Scope layout
        if scope_layout.indexOf(self.scopes) == -1:
            scope_layout.insertWidget(0, self.scopes)

        if scope_layout.indexOf(self.generate) == -1:
            scope_layout.addWidget(self.generate)

        # Browser layout
        if browser_layout.indexOf(self.label) == -1:
            browser_layout.insertWidget(0, self.label)

        if browser_layout.indexOf(self.browser) == -1:
            browser_layout.addWidget(self.browser)

        # Stacked insertion
        if self.stacked.indexOf(self.scope_container) == -1:
            self.stacked.addWidget(self.scope_container)

        if self.stacked.indexOf(self.browser_container) == -1:
            self.stacked.addWidget(self.browser_container)

    # Generator signals
    def initiate(self):
        """Initiates the OAuth flow."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()

        # Extension validation
        if 'twitch' not in app.client.extensions:  # This shouldn't happen
            self.LOGGER.warning("The twitch extension isn't loaded!")
            self.LOGGER.debug('If this converter was reimplemented by another extension, the author should consider '
                              'reviewing it.')

            self.LOGGER.debug('Creating informative dialog...')
            _m = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Warning, 'Token Generator',
                'The twitch extension must be loaded before you can generate a new token.',
                QtWidgets.QMessageBox.Ok, app.client.settings
            )

            self.LOGGER.debug('Displaying dialog...')
            _m.exec()

            self.LOGGER.debug('Ensuring dialog is deleted properly...')
            _m.deleteLater()

            return

        # Get the client ID
        try:
            self.LOGGER.debug('Getting client id from the Twitch extension...')
            client_id = app.client.settings['extensions']['twitch']['client_id'].value

        except KeyError:
            self.LOGGER.warning("The Twitch extension's settings are invalid!  Did someone modify them?")
            client_id = None

        else:
            if not client_id:
                self.LOGGER.warning("Cannot locate the Twitch extension's client id!")
                client_id = None

        # Client id validation
        if client_id is None:
            self.LOGGER.warning('There is no client id!')

            self.LOGGER.debug('Creating informative dialog...')
            _m = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Token Generator',
                'A token cannot be generated without a client id!',
                QtWidgets.QMessageBox.Ok, app.client.settings
            )

            self.LOGGER.debug('Displaying dialog...')
            _m.exec()

            self.LOGGER.debug('Ensuring dialog is deleted properly...')
            _m.deleteLater()

            return

        # Ensure the browser is visible
        if self.stacked.currentWidget() != self.browser_container:
            self.LOGGER.debug('Displaying QWebEngineView...')
            self.stacked.setCurrentWidget(self.browser_container)

            if self.browser.isHidden():
                self.browser.show()

            if self.label.isVisible():
                self.label.hide()

        # Clear any existing state
        self.LOGGER.debug('Clearing existing state, if one existed...')
        self._state = None

        # Generate a new state
        self.LOGGER.debug('Generating a new state...')
        self._state = secrets.token_urlsafe(256)

        # Gather the scopes
        s = []

        for row in range(self.scopes.count()):
            i = self.scopes.item(row)

            if i.checkState() == QtCore.Qt.Checked:
                s.append(i.text())

        # Clone the endpoint
        u = QtCore.QUrl(self.ENDPOINT)

        # Declare & assign a query to the clone
        p = QtCore.QUrlQuery()

        p.addQueryItem('force_verify', 'true')  # Since users may want to switch accounts
        p.addQueryItem('state', self._state)
        p.addQueryItem('redirect_uri', 'http://localhost')
        p.addQueryItem('response_type', 'token')
        p.addQueryItem('client_id', str(client_id))
        p.addQueryItem('scope', '+'.join(s))

        u.setQuery(p)

        # Set the browser
        self.browser.load(u)

        self.browser.show()
        self.browser.setHidden(False)

        self.browser_container.show()
        self.browser_container.setHidden(False)

    def url_watcher(self, url: QtCore.QUrl):
        """Watches the QWebEngineView for url changes."""
        if url.host() not in ['twitch.tv', 'localhost', self.ENDPOINT.host(),
                              'passport.twitch.tv'] and url.host() != '':

            self.LOGGER.warning(f'Redirected to an unsupported host!  ({url.host()})')

            self.LOGGER.debug('Creating informative dialog...')
            _m = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Token Generator',
                f'You were redirected to an unsupported host.  ({url.host()})',
                QtWidgets.QMessageBox.Ok, self
            )

            self.LOGGER.debug('Displaying dialog...')
            self.hide()
            _m.exec()

            self.LOGGER.debug('Ensuring dialog is deleted properly...')
            _m.deleteLater()

            self.browser.setUrl(QtCore.QUrl('about:blank'))
            return self.reject()

        if url.hasFragment():
            query = QtCore.QUrlQuery(url.fragment())

        else:
            query = QtCore.QUrlQuery(url.query())

        if not query.hasQueryItem('state') and url.path() != '/two_factor/new':
            self.LOGGER.warning('No state sent!')

            self.LOGGER.debug('Creating informative dialog...')
            _m = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Token Generator',
                "The state parameter wasn't passed.",
                QtWidgets.QMessageBox.Ok, self
            )

            self.LOGGER.debug('Displaying dialog...')
            self.hide()
            _m.exec()

            self.LOGGER.debug('Ensuring dialog is deleted properly...')
            if not sip.isdeleted(_m):
                _m.deleteLater()

            self.browser.setUrl(QtCore.QUrl('about:blank'))
            return self.reject()

        if query.hasQueryItem('state') and self._state != query.queryItemValue('state'):
            self.LOGGER.warning('Sent state is not our state!')

            self.LOGGER.debug('Creating informative dialog...')
            _m = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Critical, 'Token Generator',
                'Sent state is not our state.',
                QtWidgets.QMessageBox.Ok, self
            )

            self.LOGGER.debug('Displaying dialog...')
            _m.exec()
            self.hide()

            self.LOGGER.debug('Ensuring dialog is deleted properly...')
            _m.deleteLater()

            self.browser.setUrl(QtCore.QUrl('about:blank'))
            return self.reject()

        if query.hasQueryItem('access_token'):
            # Declarations
            app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
            client_id = app.client.settings['extensions']['twitch']['client_id'].value
            scopes: typing.List[Scopes] = [Scopes(s) for s in parse.unquote(query.queryItemValue('scope')).split('+')]

            self.GENERATED.emit(token.Token(client_id, query.queryItemValue('access_token'), scopes))
            self.accept()
