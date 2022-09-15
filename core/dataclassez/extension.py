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
import collections
import dataclasses
import inspect
import logging
import pathlib
import typing

import sys
from PySide2 import QtCore, QtWidgets

from utils import enums

__all__ = ['Extension', 'ExtensionStub']

if typing.TYPE_CHECKING:
    from core import widgets
    from core.utils.custom import QApp


    class ExtensionStub(typing.NamedTuple):
        NAME: str
        PATH: pathlib.Path

# Stub declaration
# noinspection PyTypeChecker
ExtensionStub = collections.namedtuple('ExtensionUnloaded', ['NAME', 'PATH'])


# noinspection PyBroadException
@dataclasses.dataclass()
class Extension(QtCore.QObject):
    """A soft wrapper around extensions."""
    # Signals
    stateChanged: typing.ClassVar[QtCore.Signal] = QtCore.Signal(object)
    metaUpdated: typing.ClassVar[QtCore.Signal] = QtCore.Signal()

    # before, after
    displayNameChanged: typing.ClassVar[QtCore.Signal] = QtCore.Signal(str, str)
    versionChanged: typing.ClassVar[QtCore.Signal] = QtCore.Signal(str, str)
    authorsChanged: typing.ClassVar[QtCore.Signal] = QtCore.Signal(set, set)
    websiteChanged: typing.ClassVar[QtCore.Signal] = QtCore.Signal(QtCore.QUrl, QtCore.QUrl)
    documentationChanged: typing.ClassVar[QtCore.Signal] = QtCore.Signal(QtCore.QUrl, QtCore.QUrl)

    # Class attributes
    NAME: typing.ClassVar[str]
    DISPLAY_NAME: typing.ClassVar[str]
    VERSION: typing.ClassVar[QtCore.QVersionNumber] = QtCore.QVersionNumber(1, 0, 0)
    AUTHORS: typing.ClassVar[typing.Set[str]] = {'Unknown'}
    LOGGER: typing.ClassVar[logging.Logger]
    WEBSITE: typing.ClassVar[QtCore.QUrl]
    DOCUMENTATION: typing.ClassVar[QtCore.QUrl]
    STATE: typing.ClassVar[enums.ExtensionStates] = enums.ExtensionStates.LOADED

    # Instance attributes
    client: 'widgets.Client' = dataclasses.field(init=False)
    widget: 'widgets.About' = dataclasses.field(init=False)

    # Internal attributes
    # Used reflectively
    __imports: typing.List[str] = dataclasses.field(init=False, default_factory=list)
    __package: str = dataclasses.field(init=False)
    __path: pathlib.Path = dataclasses.field(init=False)

    # Init variables
    parent: dataclasses.InitVar[QtCore.QObject] = None

    def __post_init__(self, parent: QtCore.QObject = None):
        # Super Call #
        super(QtCore.QObject, self).__init__(parent=parent)

        # Assignments
        self.client = QtWidgets.QApplication.instance().client

        # Validation
        self.NAME = self.__class__.__name__.lower()
        self.LOGGER = logging.getLogger(f'extensions.{self.NAME}')

        # Ensure there's always a display name attribute
        try:
            _ = self.DISPLAY_NAME

        except AttributeError:
            self.set_display_name(self.NAME.title())

        # Ensure there's always a website attribute
        try:
            _ = self.WEBSITE

        except AttributeError:
            self.set_website(QtCore.QUrl())

        # Ensure there's always a documentation attribute
        try:
            _ = self.DOCUMENTATION

        except AttributeError:
            self.set_documentation(QtCore.QUrl())

        QtCore.QTimer.singleShot(1, self.generate_dialog)

    # Ui methods
    def generate_dialog(self):
        pass

    # State methods
    def set_state(self, state: enums.ExtensionStates):
        """A convenience method for setting the extension state, and emitting
        the `STATE_CHANGED` signal."""
        self.STATE = state
        self.stateChanged.emit(state)

    # Lifecycle methods
    def setup(self):
        """Sets up the extension."""
        # Setup sequence
        self.LOGGER.info(f'Setting up {self.DISPLAY_NAME}...')
        self.set_state(enums.ExtensionStates.SET_UP)
        self.LOGGER.info(f'{self.DISPLAY_NAME} successfully set up!')

        raise NotImplementedError

    def teardown(self):
        """Tears down the extension."""
        # Tear down sequence
        self.LOGGER.warning(f'Tearing down {self.DISPLAY_NAME}...')

        self.LOGGER.warning(f'Cleaning up QObjects...')
        for attr, inst in inspect.getmembers(self):
            # Ensure we don't forcibly delete the bot
            if inst == self.client:
                continue

            if isinstance(inst, QtWidgets.QWidget):
                # Ensure we don't forcibly delete bot's resources
                if inst.parent() == self.client or inst.parentWidget() == self.client:
                    continue

                self.LOGGER.debug(f'Calling {self.__class__.__name__}.{attr}::close ...')
                inst.close()

                self.LOGGER.debug(f'Calling {self.__class__.__name__}.{attr}::deleteLater ...')
                inst.deleteLater()

            elif isinstance(inst, QtCore.QObject):
                # Ensure we don't forcibly delete bot's resources
                if inst.parent() == self.client:
                    continue

                self.LOGGER.debug(f'Calling {self.__class__.__name__}.{attr}::deleteLater ...')
                inst.deleteLater()

        # Update state
        self.set_state(enums.ExtensionStates.TORN_DOWN)
        self.LOGGER.info(f'{self.DISPLAY_NAME} successfully torn down!')

    def unload(self) -> ExtensionStub:
        """Unloads the extension."""
        # Declarations
        # noinspection PyTypeChecker
        app: 'QApp' = QtWidgets.QApplication.instance()
        imports = getattr(self, f'_{self.__class__.__name__}__imports', [])
        path = getattr(self, f'_{self.__class__.__name__}__path')

        # Unloading sequence
        self.LOGGER.warning(f'Unloading {self.DISPLAY_NAME}...')

        # Tear down the extension if it isn't
        if self.STATE != enums.ExtensionStates.TORN_DOWN:
            self.teardown()

        # Filter shared libraries
        my_imports = imports.copy()

        for ext in app.client.extensions.values():
            if ext.NAME == self.NAME or isinstance(ext, ExtensionStub):
                continue  # We already have our imports & stubs can't have imports

            # Filter our imports by shared imports
            for i in getattr(ext, f'_{ext.__class__.__name__}__imports', []):
                if i in my_imports:
                    my_imports.remove(i)

        # "Remove" modules this extension loaded
        for key in my_imports:
            if key in sys.modules:
                del sys.modules[key]

        # Update state
        self.set_state(enums.ExtensionStates.UNLOADED)
        self.LOGGER.info(f'{self.DISPLAY_NAME} successfully unloaded!')

        # Return the stub
        return ExtensionStub(self.NAME, path)

    # Utility methods
    def set_display_name(self, name: str):
        """Sets the display name for `extension`."""
        prior = getattr(self, 'DISPLAY_NAME', '')

        self.displayNameChanged.emit(prior, name)
        self.DISPLAY_NAME = name

    def set_version(self, *version: int):
        """Sets the version for `extension`."""
        self.versionChanged.emit('.'.join([str(i) for i in self.VERSION]), '.'.join([str(i) for i in version]))
        self.VERSION = QtCore.QVersionNumber(*version)

    def set_authors(self, *authors: str):
        """Sets the authors for `extension`."""
        a = set(authors)

        self.authorsChanged.emit(self.AUTHORS, a)
        self.AUTHORS = a

    def set_website(self, website: typing.Union[QtCore.QUrl, str]):
        """Sets the website for `extension`."""
        prior = getattr(self, 'WEBSITE', QtCore.QUrl())
        w = QtCore.QUrl(website)

        self.websiteChanged.emit(prior, w)
        self.WEBSITE = w

    def set_documentation(self, website: typing.Union[QtCore.QUrl, str]):
        """Sets the documentation website for `extension`."""
        prior = getattr(self, 'DOCUMENTATION', QtCore.QUrl())
        d = QtCore.QUrl(website)

        self.documentationChanged.emit(prior, d)
        self.DOCUMENTATION = d

    # Magic Methods #
    def __repr__(self):
        return f'<{self.__class__.__name__} name="{self.NAME}" version="{".".join([str(i) for i in self.VERSION])}">'
