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
import inspect
import typing
from typing import Dict, List, Tuple

from PySide2 import QtCore, QtGui, QtWidgets

from QtTwitch import gateway, http, parser
from QtUtilities import settings as qsettings
from core import dataclassez
from core.utils import enums as core_enums
from . import dataclasses as twitch_dataclasses, enums as twitch_enums
from .settings import converters

__all__ = ['Twitch']


class Twitch(dataclassez.Platform, dataclassez.Modifier):
    """The core of the Twitch extension."""
    # Signals
    TOKEN_CHANGED = QtCore.Signal(object)  # Token instance

    # Class attributes
    DISPLAY_NAME = 'Twitch for ShovelBot'
    VERSION = QtCore.QVersionNumber(1, 0, 0)
    AUTHORS = {'SirRandoo'}
    WEBSITE = QtCore.QUrl('https://github.com/sirrandoo/twitch-for-shovelbot')
    DOCUMENTATION = QtCore.QUrl('https://sirrandoo.github.io/projects/twitch-for-shovelbot')

    def __post_init__(self, parent: QtCore.QObject = None):
        # Super Call #
        super(Twitch, self).__post_init__(parent=parent)

        # Get the shared resources
        # noinspection PyTypeChecker

        # Public attributes
        self.irc = gateway.Gateway()
        self.http: typing.Optional[http.Http] = None

        # Internal attributes
        self._scopes: Dict[str, List[Tuple[twitch_enums.Scopes, str]]] = {}
        self._scope_timer: QtCore.QTimer = QtCore.QTimer(parent=self)

        # Stitching
        self.client.aboutToStart.connect(self.prepare_connection)
        self.client.aboutToStop.connect(self.destroy_connection)
        self.irc.on_message.connect(self.transform_message)
        # self.irc.on_message.connect(functools.partial(print, 'IRC DEBUG >'))

    # Token methods
    def process_token(self):
        """Handles new tokens."""

    # Connection methods
    def prepare_connection(self):
        """Prepares the IRC connection to Twitch's servers."""
        self.LOGGER.info("Preparing connection to Twitch's IRC servers...")
        channel = self.client.settings['extensions']['twitch']['channel'].value

        if not self.irc.is_connected():
            self.irc.channels.clear()

            if channel:
                self.irc.channels = [channel]

            self.LOGGER.info('Establishing connection...')
            self.irc.connect()

        else:
            self.LOGGER.warning("Already connected to Twitch's IRC servers!")

            if channel:
                self.LOGGER.warning('Leaving all channels...')

                for c in [c for c in self.irc.channels if c.lower() != channel.lower()]:
                    self.irc.part(c)

                if channel.lower() not in self.irc.channels:
                    self.LOGGER.info(f'Connecting to #{channel}...')
                    self.irc.join(channel)

    def destroy_connection(self):
        """Destroys the connection to Twitch's IRC servers."""
        if self.irc.is_connected():
            self.LOGGER.warning("Disconnecting from Twitch's IRC servers...")

            self.irc.disconnect()
            self.irc.channels.clear()

    def send_message(self, message: str):
        """Sends a message to Twitch's IR servers."""
        self.irc.send_priv_message(self.client.settings['extensions']['twitch']['channel'].value, message)

    # Generator methods
    def register_scope(self, extension_name: str, scope: str, reason: str = None):
        """Registers `scope` to `extension_name` for `reason`.  This method
        automatically prompts the user to authorize your scopes.  If the user
        accepts, they will be redirected to the OAuth flow again."""
        # Conversion
        s = twitch_enums.Scopes(scope)

        # Validation
        if extension_name not in self._scopes:
            self._scopes[extension_name] = []

        # Insertion
        self._scopes[extension_name].append((s, reason))

        # Timer refresh
        if self._scope_timer.isActive():
            self._scope_timer.stop()

        self._scope_timer.start(5 * 1000)  # Inform the user after 5 seconds

    def unregister_scope(self, extension_name: str, scope: str):
        """Unregisters `scope` from `extension_name`.  This method automatically
        prompts the user to generate a new token without the scope specified.
        If the user accepts, they will be redirected to the OAuth flow again."""
        # Conversion
        s = twitch_enums.Scopes(scope)

        # Validation
        if extension_name not in self._scopes:
            self._scopes[extension_name] = []

        for index, scope, reason in enumerate(self._scopes[extension_name].copy()):
            if s.name == scope.name:
                self._scopes[extension_name].pop(index)
                break

        # Timer refresh
        if self._scope_timer.isActive():
            self._scope_timer.stop()

        self._scope_timer.start(5 * 1000)  # Inform the user after 5 seconds

    # Settings methods
    def register_converters(self):
        """Registers Twitch-specific converters to the settings dialog."""
        self.LOGGER.info('Registering converters...')
        for name, inst in inspect.getmembers(converters):
            c = f'twitch.{name}'

            if inspect.isfunction(inst):
                if c in self.client.settings.converters:
                    self.LOGGER.warning(f'Converter {c} is already registered!  Overwriting...')
                    container = inspect.getmodule(self.client.settings.converters[c])

                    if container:
                        self.LOGGER.debug(f'Converter {c} pre-overwrite belongs to {container.__name__}!')

                    else:
                        self.LOGGER.debug(f"Could not locate converter's origin!")

                self.LOGGER.debug(f'Registering converter {c} to {converters.__package__}.{name}')
                self.client.settings.converters[c] = inst

        self.LOGGER.info('Converters registered!')

    def register_settings(self):
        """Registers Twitch-specific settings to the settings dialog."""
        self.LOGGER.debug('Checking existence of Twitch settings...')

        if 'twitch' not in self.client.settings['extensions']:
            self.LOGGER.warning('Twitch settings do not exist!  Generating defaults...')

            self.LOGGER.debug('Creating "twitch" setting category...')
            t = qsettings.Setting('twitch', tooltip='Settings related to the Twitch extension.')

            self.LOGGER.debug('Adding settings to twitch setting category...')
            t.add_children(*self.generate_settings())

            self.LOGGER.debug('Adding twitch setting category to extension category...')
            self.client.settings['extensions'].add_child(t)

        else:
            self.LOGGER.warning('Twitch settings exist!  Validating settings...')
            self.validate_settings()

        self.stitch_settings()

    def stitch_settings(self):
        """Stitches the settings' signals to their respective slots."""
        # Account settings
        self.client.settings['extensions']['twitch']['token'].value_changed.connect(self.TOKEN_CHANGED.emit)

        self.client.settings['extensions']['twitch']['token'].value_changed.connect(self.sync_settings)
        self.client.settings['extensions']['twitch']['client_id'].value_changed.connect(self.sync_settings)
        self.client.settings['extensions']['twitch']['channel'].value_changed.connect(self.sync_settings)

    def validate_settings(self):
        """Validates the extension's settings."""

    @staticmethod
    def generate_settings() -> typing.List[qsettings.Setting]:
        """Generates a default list of settings for the Twitch extension."""
        # Declarations
        top = {
            # Settings
            'client_id': qsettings.Setting('client_id', '', display_name='Client ID',
                                           tooltip='The client id the Twitch extension will use for API requests.'),
            'channel': qsettings.Setting('channel', '', tooltip='The channel to connect to.'),

            'token': qsettings.Setting('token', '', converter='twitch.token',
                                       tooltip="The OAuth token to connect to chat with.  If one isn't provided, "
                                               "the bot will connect anonymously.")
        }

        # Return values
        return list(top.values())

    # Token methods
    def set_token(self, token: twitch_dataclasses.Token):
        """A convenience function for setting the token the Twitch extension
        will use for authentication purposes."""
        # Set the setting's internals to the new token
        self.client.settings['extensions']['twitch']['account']['token'].set_value(token.data)
        self.client.settings['extensions']['twitch']['account']['token'].data['scopes'] = [s.value for s in
                                                                                           token.scopes]

        # Set the QLineEdit's text to the token
        try:
            view = self.client.settings.view['extensions/twitch/account/token']

        except KeyError:
            self.LOGGER.warning("The settings dialog hasn't been set up yet!")
            raise LookupError("The settings dialog hasn't been set up yet!")

        else:
            if view.display is None or view.display.layout() is None:
                self.LOGGER.warning("The token setting's display hasn't been set up yet!")
                raise LookupError(f"The token setting's display hasn't been set up yet!")

            for child in view.display.layout().children():
                if isinstance(child, QtWidgets.QLineEdit):
                    return child.set_text(token.data)

        finally:
            self.process_token()

    # Slots
    def sync_settings(self):
        """Syncs setting changes with objects the Twitch extension uses."""
        channel = self.client.settings['extensions']['twitch']['channel'].value
        token = self.client.settings['extensions']['twitch']['token'].value
        login = None

        self.http.token = token
        self.http.client_id = self.client.settings['extensions']['twitch']['client_id'].value

        if token is not None and token != '':
            response = self.http.validate_token(token)
            login = response['login']
            self.client.settings['extensions']['twitch']['token'].data['scopes'] = response.get('scopes', [])

            # Set the QLineEdit's text to the token
            # TODO: This could potentially cause issues with process_token
            try:
                view = self.client.settings.view['extensions/twitch/token']

            except KeyError:
                self.LOGGER.warning("The settings dialog hasn't been set up yet!")
                raise LookupError("The settings dialog hasn't been set up yet!")

            else:
                if view.display is None or view.display.layout() is None:
                    self.LOGGER.warning("The token setting's display hasn't been set up yet!")
                    raise LookupError(f"The token setting's display hasn't been set up yet!")

                for child in view.display.layout().children():
                    if isinstance(child, QtWidgets.QLineEdit):
                        child.setToolTip('Current scopes: {}'.format(', '.join(response.get('scopes', []))))
                        break

            finally:
                self.process_token()

        elif token == '':
            login = 'justinfan3892'
            token = 'foobar'

        if self.irc.nick.lower() != login.lower() or self.irc.token != token.lower():
            self.irc.set_credentials(login, token)

        if self.irc.is_connected() and channel.lower() not in self.irc.channels:
            # Leave every channel the client is currently in
            # The client should only ever be in one channel.
            for c in self.irc.channels:
                self.irc.part(c)

            # Join the new channel
            if channel:
                self.irc.join(channel)

    def transform_message(self, message: str):
        """Transform a QtTwitch message string into a Message dataclass."""
        print(message.strip())
        m = parser.Parser.PATTERN.match(message.strip())

        if not m:
            return self.LOGGER.warning(f'Could not parse message "{message}"')

        components = m.groupdict()

        if components['command'] == 'PRIVMSG':
            tags = {}

            if 'tags' in components:
                for segment in components['tags'].split(';'):
                    parts = segment.split('=')

                    try:
                        tags[parts[0]] = parts[1]

                    except IndexError:
                        tags[parts[0]] = ""

            username = components['prefix'].split('!')[0]
            display_name = tags.get('display-name', username.title())
            color = QtGui.QColor(tags.get('color', '#262626'))
            badge_str = tags.get('badges', '')

            mod = 'moderator' in badge_str or 'global_mod' in badge_str or 'staff' in badge_str \
                  or 'broadcaster' in badge_str or 'admin' in badge_str

            user = dataclassez.User(username, display_name, color, mod)
            message = dataclassez.Message(components['params'].split(' ')[-1].lstrip(':'), user)

            self.onMessage.emit(message)

    # Extension overrides
    def setup(self):
        """Sets up the Twitch extension."""
        self.LOGGER.info(f'Setting up {self.DISPLAY_NAME}...')

        # Register setting converters
        self.register_converters()

        # Register settings
        self.register_settings()

        # noinspection PyAttributeOutsideInit
        self.http = http.Http(self.client.settings['extensions']['twitch']['client_id'].value,
                              factory=self.client.request_factory)

        # Mark the Twitch extension as set up
        self.set_state(core_enums.ExtensionStates.SET_UP)

    def teardown(self):
        """Tears down the Twitch extension."""

    # Modifier overrides
    def should_modify(self, platform: dataclassez.Platform) -> bool:
        """An override to ensure the Twitch extension only modifies messages
        from itself."""
        return isinstance(platform, self)

    def modify(self, message: dataclassez.Message) -> dataclassez.Message:
        """Modifies the message's contents to ensure Twitch elements, such as
        emoticons, are properly displayable in the client's chat window."""
        return message
