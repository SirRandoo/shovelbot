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
import typing

from PySide6 import QtHelp, QtWidgets, QtGui


class Help(QtWidgets.QDialog):
    """A custom dialog for displaying ShovelBot's help manual."""

    def __init__(self, **kwargs):
        # Super Call #
        super(Help, self).__init__(parent=kwargs.get("parent"))

        # Ui Declarations #
        self.display: typing.Optional[QtWidgets.QTextBrowser] = None
        self.search: typing.Optional[QtWidgets.QLineEdit] = None
        self.search_button: typing.Optional[QtWidgets.QPushButton] = None
        self.search_insensitive: typing.Optional[QtWidgets.QCheckBox] = None
        self.search_whole: typing.Optional[QtWidgets.QCheckBox] = None
        self.search_backward: typing.Optional[QtWidgets.QCheckBox] = None
        self.search_auto: typing.Optional[QtWidgets.QCheckBox] = None
        self.search_container: typing.Optional[QtWidgets.QWidget] = None
        self.search_augment_container: typing.Optional[QtWidgets.QWidget] = None
        self.search_box: typing.Optional[QtWidgets.QWidget] = None

        self.find_action: typing.Optional[QtGui.QAction] = None

        # "Private" Attributes #
        self._engine: QtHelp.QHelpEngineCore = kwargs.pop("engine")

        # Internal Calls #
        self.setup_ui()

        self.find_action.triggered.connect(self.toggle_search)
        self.addAction(self.find_action)

    # Ui Methods #
    def setup_ui(self):
        """Sets up the UI for the help dialog."""
        if self.find_action is None:
            self.find_action = QtGui.QAction('Find')
            self.find_action.setShortcut(QtGui.QKeySequence('CTRL+F'))

        if self.display is None:
            self.display = QtWidgets.QTextBrowser()
            self.display.setReadOnly(True)

        if self.search is None:
            self.search = QtWidgets.QLineEdit()

        if self.search_button is None:
            self.search_button = QtWidgets.QPushButton('Search')

        if self.search_container is None:
            self.search_container = QtWidgets.QWidget()

        if self.search_box is None:
            self.search_box = QtWidgets.QWidget()

        if self.search_augment_container is None:
            self.search_augment_container = QtWidgets.QWidget()

        if self.search_insensitive is None:
            self.search_insensitive = QtWidgets.QCheckBox('Insensitive?')

        if self.search_whole is None:
            self.search_whole = QtWidgets.QCheckBox('Whole Word?')

        if self.search_backward is None:
            self.search_backward = QtWidgets.QCheckBox('Backwards?')

        if self.search_auto is None:
            self.search_auto = QtWidgets.QCheckBox('Auto Search?')

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.search_box)
        layout.addWidget(self.display)

        box_layout = QtWidgets.QVBoxLayout(self.search_box)
        box_layout.addWidget(self.search_container)
        box_layout.addWidget(self.search_augment_container)
        box_layout.setContentsMargins(2, 2, 2, 2)

        search_layout = QtWidgets.QHBoxLayout(self.search_container)
        search_layout.addWidget(self.search)
        search_layout.addWidget(self.search_button)
        search_layout.setContentsMargins(0, 0, 0, 0)

        augment_layout = QtWidgets.QHBoxLayout(self.search_augment_container)
        augment_layout.addWidget(self.search_backward)
        augment_layout.addWidget(self.search_insensitive)
        augment_layout.addWidget(self.search_whole)
        augment_layout.addWidget(self.search_auto)
        augment_layout.setContentsMargins(0, 0, 0, 0)
        augment_layout.setSpacing(2)

        self.search_box.setHidden(True)

    def toggle_search(self):
        """Toggles the search box."""
        if self.search_box.isHidden():
            self.search_box.setHidden(False)

        else:
            self.search_box.setHidden(True)
