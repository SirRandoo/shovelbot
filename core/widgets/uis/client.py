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
import functools
import inspect
import logging
import typing

from PySide6 import QtCore, QtWidgets

from QtUtilities.widgets import QTable
from core.utils import enums
from core import dataclassez
from ..chat import Chat

if typing.TYPE_CHECKING:
    from core.utils.custom import QApplication

__all__ = ['Client']


class Client:
    """A dedicated class to house the client's QWidgets."""
    LOGGER = logging.getLogger('core.ui')

    def __init__(self):
        # Top-level widgets
        self.central_tabs: typing.Optional[QtWidgets.QTabWidget] = None

        # Top-level menubar widgets
        self.file_menu: typing.Optional[QtWidgets.QMenu] = None
        self.help_menu: typing.Optional[QtWidgets.QMenu] = None

        # File menu actions
        self.halt_action: typing.Optional[QtWidgets.QAction] = None
        self.stop_action: typing.Optional[QtWidgets.QAction] = None
        self.quit_action: typing.Optional[QtWidgets.QAction] = None
        self.start_action: typing.Optional[QtWidgets.QAction] = None
        self.settings_action: typing.Optional[QtWidgets.QAction] = None

        # Help menu actions
        self.help_action: typing.Optional[QtWidgets.QAction] = None
        self.about_action: typing.Optional[QtWidgets.QAction] = None
        self.update_action: typing.Optional[QtWidgets.QAction] = None

        # Central tabs
        self.stream_tab: typing.Optional[QtWidgets.QMainWindow] = None
        self.extensions_tab: typing.Optional[QtWidgets.QWidget] = None

        # Stream widgets
        self.stream_chat: typing.Optional[Chat] = None

        # Extensions widgets
        self.extension_menu: typing.Optional[QtWidgets.QMenu] = None
        self.extension_load: typing.Optional[QtWidgets.QAction] = None
        self.extension_unload: typing.Optional[QtWidgets.QAction] = None
        self.extension_details: typing.Optional[QtWidgets.QAction] = None
        self.extension_visibility: typing.Optional[QtWidgets.QAction] = None
        self.extensions_table: typing.Optional[QTable] = None

    # Setup methods
    def setup(self, parent: QtWidgets.QMainWindow):
        """Sets up the client's UI"""
        parent.statusBar()

        # Menubar elements
        self.setup_menubar(parent)
        self.setup_file_menu()
        self.setup_help_menu()

        # Tabs
        self.setup_central_widget(parent)
        self.setup_central_tabs()

        # Stream elements
        self.setup_stream_tab()

        # Extension elements
        self.setup_extensions_tab()

    def setup_central_widget(self, parent: QtWidgets.QMainWindow):
        """Sets up the client's UI elements."""
        if should_create_widget(self.central_tabs):
            self.central_tabs = QtWidgets.QTabWidget()
            self.central_tabs.setTabPosition(QtWidgets.QTabWidget.west)
            self.central_tabs.setDocumentMode(True)
            self.central_tabs.setMovable(True)

        # Insert them
        if parent.centralWidget() != self.central_tabs:
            parent.setCentralWidget(self.central_tabs)

    def setup_menubar(self, parent: QtWidgets.QMainWindow):
        """Sets up the client's menubar."""
        menubar: QtWidgets.QMenuBar = parent.menuBar()

        # Generate menubar elements
        if should_create_widget(self.file_menu):
            self.file_menu = QtWidgets.QMenu('File')

        if should_create_widget(self.help_menu):
            self.help_menu = QtWidgets.QMenu('Help')

        # Insert them
        if self.file_menu.menuAction() not in menubar.actions():
            menubar.insertMenu(self.help_menu.menuAction(), self.file_menu)

        if self.help_menu.menuAction() not in menubar.actions():
            menubar.addMenu(self.help_menu)

    def setup_file_menu(self):
        """Sets up the file menu."""
        if should_create_widget(self.halt_action):
            self.halt_action = QtWidgets.QAction('Halt ShovelBot')
            self.halt_action.setToolTip('Halts ShovelBot')
            self.halt_action.setShortcut('CTRL+H')

        if should_create_widget(self.stop_action):
            self.stop_action = QtWidgets.QAction('Stop ShovelBot')
            self.stop_action.setToolTip('Stops ShovelBot')
            self.stop_action.setShortcut('ALT+S')

        if should_create_widget(self.start_action):
            self.start_action = QtWidgets.QAction('Start ShovelBot')
            self.start_action.setToolTip('Starts ShovelBot')
            self.start_action.setShortcut('CTRL+S')

        if should_create_widget(self.quit_action):
            self.quit_action = QtWidgets.QAction('Quit')

            self.quit_action.setShortcut('CTRL+Q')
            self.quit_action.setToolTip('Quits ShovelBot')
            self.quit_action.setMenuRole(QtWidgets.QAction.QuitRole)

        if should_create_widget(self.settings_action):
            self.settings_action = QtWidgets.QAction('Settings...')

            self.settings_action.setShortcut('CTRL+SHIFT+S')
            self.settings_action.setToolTip('Opens the settings dialog')
            self.settings_action.setMenuRole(QtWidgets.QAction.PreferencesRole)

        if self.start_action not in self.file_menu.actions():
            self.file_menu.insertAction(self.halt_action, self.start_action)

        if self.halt_action not in self.file_menu.actions():
            self.file_menu.insertAction(self.stop_action, self.halt_action)

        if self.stop_action not in self.file_menu.actions():
            self.file_menu.insertAction(self.settings_action, self.stop_action)
            self.file_menu.insertSeparator(self.settings_action)

        if self.settings_action not in self.file_menu.actions():
            self.file_menu.insertAction(self.quit_action, self.settings_action)
            self.file_menu.insertSeparator(self.quit_action)

        if self.quit_action not in self.file_menu.actions():
            self.file_menu.addAction(self.quit_action)

    def setup_help_menu(self):
        """Sets up the help menu."""
        if should_create_widget(self.help_action):
            self.help_action = QtWidgets.QAction('Help...')

            self.help_action.setShortcut('F1')
            self.help_action.setToolTip('Opens the help manual')
            self.help_action.setMenuRole(QtWidgets.QAction.ApplicationSpecificRole)

        if should_create_widget(self.about_action):
            self.about_action = QtWidgets.QAction('About...')

            self.about_action.setShortcut('F3')
            self.about_action.setToolTip('Opens the about dialog.')
            self.about_action.setMenuRole(QtWidgets.QAction.AboutRole)

        if should_create_widget(self.update_action):
            self.update_action = QtWidgets.QAction('Check for Updates...')

            self.update_action.setShortcut('F2')
            self.update_action.setToolTip('Checks for client and extension updates')
            self.update_action.setMenuRole(QtWidgets.QAction.ApplicationSpecificRole)

        if self.help_action not in self.help_menu.actions():
            self.help_menu.insertAction(self.about_action, self.help_action)
            self.help_menu.insertSeparator(self.about_action)

        if self.about_action not in self.help_menu.actions():
            self.help_menu.insertAction(self.update_action, self.about_action)

        if self.update_action not in self.help_menu.actions():
            self.help_menu.addAction(self.update_action)

    def setup_central_tabs(self):
        """Sets up the central tabs."""
        if should_create_widget(self.stream_tab):
            self.stream_tab = QtWidgets.QMainWindow(flags=QtCore.Qt.Widget)
            widget = QtWidgets.QWidget(flags=QtCore.Qt.Widget)

            widget.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)

            self.stream_tab.setCentralWidget(widget)
            self.stream_tab.setDockNestingEnabled(True)

        if should_create_widget(self.extensions_tab):
            self.extensions_tab = QtWidgets.QWidget(flags=QtCore.Qt.Widget)

        widgets = [self.central_tabs.widget(w) for w in range(self.central_tabs.count())]
        if self.stream_tab not in widgets:
            self.central_tabs.addTab(self.stream_tab, 'Stream')

        if self.extensions_tab not in widgets:
            self.central_tabs.addTab(self.extensions_tab, 'Extensions')

    def setup_stream_tab(self):
        """Sets up the stream tab."""
        if should_create_widget(self.stream_chat):
            self.stream_chat = Chat()

        self.stream_tab.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.stream_chat)

    def setup_extensions_tab(self):
        """Sets up the extensions tab."""
        if should_create_widget(self.extensions_table):
            self.extensions_table = QTable()

            self.extensions_table.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
            self.extensions_table.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.extensions_table.setAlternatingRowColors(True)
            self.extensions_table.setDropIndicatorShown(False)
            self.extensions_table.setAcceptDrops(False)
            self.extensions_table.setWordWrap(True)

            self.extensions_table.horizontalHeader().setStretchLastSection(True)
            self.extensions_table.horizontalHeader().setSortIndicatorShown(True)
            self.extensions_table.verticalHeader().setHidden(True)

            self.extensions_table.setColumnCount(3)
            self.extensions_table.set_horizontal_headers('Name', 'Version', 'State')

        if should_create_widget(self.extension_menu):
            self.extension_menu = QtWidgets.QMenu()

        if should_create_widget(self.extension_load):
            self.extension_load = QtWidgets.QAction('Load')

        if should_create_widget(self.extension_unload):
            self.extension_unload = QtWidgets.QAction('Unload')

        if should_create_widget(self.extension_details):
            self.extension_details = QtWidgets.QAction('Details')

        if should_create_widget(self.extension_visibility):
            self.extension_visibility = QtWidgets.QAction('Hide Unloaded')
            self.extension_visibility.setCheckable(True)

        if self.extension_details not in self.extension_menu.actions():
            self.extension_menu.insertAction(self.extension_load, self.extension_details)
            self.extension_menu.insertSeparator(self.extension_load)

        if self.extension_load not in self.extension_menu.actions():
            self.extension_menu.insertAction(self.extension_unload, self.extension_load)

        if self.extension_unload not in self.extension_menu.actions():
            self.extension_menu.insertAction(self.extension_visibility, self.extension_unload)
            self.extension_menu.insertSeparator(self.extension_visibility)

        if self.extension_visibility not in self.extension_menu.actions():
            self.extension_menu.addAction(self.extension_visibility)

        layout = QtWidgets.QGridLayout(self.extensions_tab)
        layout.addWidget(self.extensions_table)

    # Stitch methods
    def stitch(self):
        """Stitches the QWidget's signals to their respective slots."""
        for name, inst in inspect.getmembers(self):
            if name.startswith('stitch_'):
                inst()

    def stitch_file_menu(self):
        """Stitches the file menu's signals to their respective slots."""
        # Declarations
        app: QApplication = QtWidgets.QApplication.instance()

        # Stitching
        self.LOGGER.debug('Stitching `start_action.triggered` to `client.start_bot`')
        self.start_action.triggered.connect(app.client.start_bot)

        self.LOGGER.debug('Stitching `halt_action.triggered` to `client.halt_bot`')
        self.halt_action.triggered.connect(app.client.halt_bot)

        self.LOGGER.debug('Stitching `stop_action.triggered` to `client.stop_bot`')
        self.stop_action.triggered.connect(app.client.stop_bot)

        self.LOGGER.debug('Stitching `settings_action.triggered` to `client.settings.show`')
        self.settings_action.triggered.connect(app.client.settings.show)

        self.LOGGER.debug('Stitching `quit_action.triggered` to `client.close`')
        # noinspection PyTypeChecker
        self.quit_action.triggered.connect(app.client.close)

    def stitch_help_menu(self):
        """Stitches the help menu's signals to their respective slots."""
        # Declarations
        app: QApplication = QtWidgets.QApplication.instance()

        # Stitching
        self.LOGGER.debug('Stitching `help_action.triggered` to `client.help`')
        self.help_action.triggered.connect(app.client.help)

        self.LOGGER.debug('Stitching `about_action.triggered` to `client.about`')
        self.about_action.triggered.connect(app.client.about)

        self.LOGGER.debug('Stitching `update_action.triggered` to `client.update_check`')
        self.update_action.triggered.connect(app.client.update_check)

    def stitch_extensions_table(self):
        """Stitches the extensions table's signals to their respective slots."""
        self.LOGGER.debug('Stitching `extension_load.triggered` to `extension_context_load`')
        self.extension_load.triggered.connect(self.extension_context_load)

        self.LOGGER.debug('Stitching `extension_unload.triggered` to `extension_context_unload`')
        self.extension_unload.triggered.connect(self.extension_context_unload)

        self.LOGGER.debug('Stitching `extension_details.triggered` to `extension_context_details`')
        self.extension_details.triggered.connect(self.extension_context_details)

        self.LOGGER.debug('Stitching `extension_visibility.triggered` to `extension_context_toggle`')
        self.extension_visibility.triggered.connect(self.extension_context_toggle)

        self.LOGGER.debug('Stitching `extensions_table.customContextMenuRequested` to `extension_context_requested`')
        self.extensions_table.customContextMenuRequested.connect(self.extension_context_requested)

        self.LOGGER.debug('Stitching `extensions_table.itemChanged` to `extensions_table.resizeColumnToContents`')
        self.extensions_table.itemChanged.connect(functools.partial(self.extensions_table.resizeColumnToContents, 0))
        self.extensions_table.itemChanged.connect(functools.partial(self.extensions_table.resizeColumnToContents, 1))

    # Extension table slots
    def update_extension_display(self):
        """Updates the extension table to display the most up-to-date information."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()

        # Update sequence
        for extension in app.client.extensions:
            # Dummy data
            display_name = extension.NAME.title()
            version = (0, 0, 0)
            state = enums.ExtensionStates.UNLOADED

            # Instance check
            if isinstance(extension, dataclassez.Extension):
                # True population
                display_name = extension.DISPLAY_NAME
                version = extension.VERSION
                state = extension.STATE

            # Conversion
            version = '.'.join([str(i) for i in version])
            state = state.name.replace('_', ' ').capitalize()

            try:
                # Get the row from the internal name
                row, internal = self.extensions_table.row_from_header(extension.NAME)

            except LookupError:
                # Insert a new row
                self.extensions_table.append(display_name, version, state)
                self.extensions_table.set_row_header(self.extensions_table.rowCount() - 1, extension.NAME)

            else:
                # Update the row
                self.extensions_table.set_row(row, display_name, version, state)

        # Remove garbage rows
        for row in self.extensions_table.vertical_headers():
            if row not in app.client.extensions:
                self.extensions_table.removeRow(row.row())

    # Extension table's context menu slots
    def extension_context_requested(self, point: QtCore.QPoint):
        """Invoked when the user right-clicks the extension table."""
        if should_create_widget(self.extension_menu):
            return logging.getLogger('core.ui').warning("Extension menu doesn't exist; this shouldn't have happened!")

        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        partial: QtWidgets.QTableWidgetItem = self.extensions_table.itemAt(point)

        # Partial validation
        if partial is None:
            self.extension_load.setDisabled(True)
            self.extension_unload.setDisabled(True)
            self.extension_details.setDisabled(True)

            return self.extension_menu.popup(app.client.mapToGlobal(point))

        # More declarations
        internal: QtWidgets.QTableWidgetItem = self.extensions_table.verticalHeaderItem(partial.row())
        state = enums.ExtensionStates.UNLOADED

        if internal.text() not in app.client.extensions:
            self.LOGGER.warning(f"{internal.text()} doesn't exist in the internal extensions cache!")
            return self.LOGGER.warning(f'This should never happen unless someone modified the internals, or ShovelBot '
                                       f'had a bug.')

        else:
            ext = app.client.extensions[internal.text()]

        # Re-enable the other actions
        self.extension_details.setEnabled(True)
        self.extension_load.setEnabled(True)

        # Instance check
        if isinstance(ext, dataclassez.Extension):
            state = ext.STATE  # Update the state to the extension's true state

        # State check
        if state == enums.ExtensionStates.UNLOADED:
            self.extension_load.set_text('Load')  # You can only load an unloaded extension
            self.extension_unload.setDisabled(True)  # You can't unload an unloaded extension

        else:
            self.extension_load.set_text('Reload')  # You can reload a loaded extension
            self.extension_unload.setEnabled(True)  # You can unload a loaded extension

        return self.extension_menu.popup(app.client.mapToGlobal(point))

    def extension_context_load(self):
        """Invoked when the user clicks "load" on the extension table's context menu."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        selected: typing.List[QtWidgets.QTableWidgetItem] = self.extensions_table.selectedItems()

        # Individually load all selected extensions
        for selection in selected:
            row: int = selection.row()
            item: QtWidgets.QTableWidgetItem = self.extensions_table.verticalHeaderItem(row)
            name: str = item.text()

            if name not in app.client.extensions:
                self.LOGGER.warning(f"Extension {name} doesn't exist in the internal extension cache!")
                continue

            else:
                stub: dataclassez.ExtensionStub = app.client.extensions[name]

            # Sequence check
            if isinstance(stub, dataclassez.Extension):  # Instance check
                if self.extension_load.text().lower() != 'reload':
                    return self.LOGGER.warning(f"Extension {stub.DISPLAY_NAME} is already loaded!")

                stub: dataclassez.Extension

                try:
                    # Unloading sequence
                    st = stub.unload()

                except NotImplementedError:
                    self.LOGGER.debug(f'{stub.DISPLAY_NAME} does not implement an unload method!')

                else:
                    # Update the extension display
                    self.extensions_table.set_row(row, State=enums.ExtensionStates.UNLOADED.name)

                    # Store the stub in the extensions list
                    for key, value in app.client.extensions.copy().items():
                        if key == stub.NAME:
                            app.client.extensions[key] = stub
                            break

                    stub = st

            # Loading sequence
            extensions = app.client.load_from_stub(stub)

            for extension in extensions:
                # Ensure the extension was loaded before continuing
                if extension is None:
                    continue  # `load_from_stub` covers the logging statements

                # Update the extension display
                self.extensions_table.set_row(row, State=extension.STATE.name.replace('_', ' ').capitalize())

                # Replace the stub with the extension instance
                app.client.extensions[stub.NAME] = extension

                # Clean up the cache
                for key, value in app.client.extensions.copy().items():
                    if value == stub and key != stub.NAME:
                        self.LOGGER.debug(f'Extension {key} already exists as {stub.DISPLAY_NAME} ({stub.NAME})!')
                        self.LOGGER.debug('This should only happen if an extension changed their internal name!')
                        del app.client.extensions[key]

                # Tell the extension it should start setting up
                self.LOGGER.debug('Informing extension that it should set up...')

                try:
                    extension.setup()

                except NotImplementedError:
                    self.LOGGER.debug(f'{extension.DISPLAY_NAME} does not implement a setup method!')

                else:
                    self.LOGGER.debug(f'{extension.DISPLAY_NAME} was successfully set up!')

                finally:
                    self.extensions_table.set_row(row, State=extension.STATE.name.replace('_', ' ').capitalize())

    def extension_context_unload(self):
        """Invoked when the user clicks "unload" on the extension table's context menu."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        selected: typing.List[QtWidgets.QTableWidgetItem] = self.extensions_table.selectedItems()

        # Individually unload all selected extensions
        for selection in selected:
            row: int = selection.row()
            item: QtWidgets.QTableWidgetItem = self.extensions_table.verticalHeaderItem(row)
            name: str = item.text()

            if name not in app.client.extensions:
                self.LOGGER.warning(f"Extension {name} doesn't exist in the internal extensions cache!")
                continue

            else:
                extension: dataclassez.Extension = app.client.extensions[name]

            # Stub instance check
            if isinstance(extension, dataclassez.ExtensionStub):
                return self.LOGGER.warning(f'Extension {extension.NAME} is already unloaded!')

            try:
                # Unloading sequence
                stub = extension.unload()

            except NotImplementedError:
                self.LOGGER.debug(f"Extension {extension.DISPLAY_NAME} doesn't implement an unload method!")

            else:
                self.extensions_table.set_row(row,
                                              State=enums.ExtensionStates.UNLOADED.name.replace('_', ' ').capitalize())
                app.client.extensions[stub.NAME] = stub

                # Clean up the extension cache
                for key, value in app.client.extensions.copy().items():
                    if value == stub and key != stub.NAME:
                        self.LOGGER.debug(f'Extension {key} already exists as {stub.NAME}!')
                        self.LOGGER.debug('This should only happen if an extension changed their internal name!')
                        del app.client.extensions[key]

    def extension_context_toggle(self):
        """Invoked when the user clicks "hide unloaded" in the extension table's
        context menu."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        checked = self.extension_visibility.isChecked()

        # Update the QAction
        self.extension_visibility.set_text('{} unloaded'.format('Show' if checked else 'Hide'))

        # Update the display
        for key, ext in app.client.extensions.items():
            try:
                row, header = self.extensions_table.row_from_header(key)

            except LookupError:
                self.LOGGER.debug(f"The extension {key} doesn't exist in the table!")

            else:
                if checked:
                    if isinstance(ext, dataclassez.ExtensionStub) or ext.STATE == enums.ExtensionStates.UNLOADED:
                        self.extensions_table.hideRow(row)

                else:
                    if self.extensions_table.isRowHidden(row):
                        self.extensions_table.showRow(row)

    def extension_context_details(self):
        """Invoked when the user clicks "details" on the extension table's context menu."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        selected: typing.List[QtWidgets.QTableWidgetItem] = self.extensions_table.selectedItems()

        # Individually show all selected extension displays
        for selection in selected:
            row: int = selection.row()
            item: QtWidgets.QTableWidgetItem = self.extensions_table.verticalHeaderItem(row)
            name: str = item.text()

            if name not in app.client.extensions:
                self.LOGGER.warning(f"Extension {name} doesn't exist in the internal extensions cache!")
                continue

            else:
                ext: dataclassez.Extension = app.client.extensions[name]

            # Stub instance check
            if isinstance(ext, dataclassez.ExtensionStub):
                return self.LOGGER.warning(f"Extension {name} isn't loaded!")

            try:
                ext.widget.show()

            except AttributeError:
                self.LOGGER.warning(f"Extension {name} hasn't implemented a widget display!")
                self.LOGGER.debug('Informing the user of what happened...')

                self.LOGGER.debug('Creating display...')
                m = QtWidgets.QMessageBox(
                    QtWidgets.QMessageBox.Warning, 'Extension Display',
                    f"{ext.DISPLAY_NAME} hasn't created a display for itself.",
                    QtWidgets.QMessageBox.Ok, app.client
                )

                if ext.WEBSITE:
                    self.LOGGER.debug('Adding a link to the extension\'s issue tracker')
                    m.setInformativeText(f"You can report this to the author "
                                         f'<a href="{ext.WEBSITE.toDisplayString()}/issues/new">here</a>')

                self.LOGGER.debug('Displaying dialog...')
                m.exec()

                self.LOGGER.debug('Ensuring dialog is properly disposed of.')
                if not sip.isdeleted(m):
                    m.deleteLater()

    # Appearance slots
    def apply_theme(self):
        """Applies the theme to the application."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        s = app.client.settings

        if s['appearance']['theme'].value == 0:
            app.setPalette(app.client.base_theme)

        else:
            try:
                p = app.client.themes[s['appearance']['theme'].value - 1]

            except IndexError:
                self.LOGGER.warning('The current theme cannot be applied.')
                app.setPalette(app.client.base_theme)

            else:
                p(app)

        # Update the chat
        p = app.palette()
        background = p.color(p.Active, p.Background)
        text = p.color(p.Active, p.Text)

        self.stream_chat.display.page().setBackgroundColor(background)
