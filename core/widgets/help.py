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
import typing

from PyQt5 import QtHelp, QtWidgets

from QtUtilities.utils import should_create_widget


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
        
        self.find_action: typing.Optional[QtWidgets.QAction] = None
        
        # "Private" Attributes #
        self._engine: QtHelp.QHelpEngineCore = kwargs.pop("engine")
        
        # Internal Calls #
        self.setup_ui()
        
        self.find_action.triggered.connect(self.toggle_search)
        self.addAction(self.find_action)
    
    # Ui Methods #
    def setup_ui(self):
        """Sets up the UI for the help dialog."""
        if should_create_widget(self.find_action):
            self.find_action = QtWidgets.QAction('Find')
            self.find_action.setShortcut('CTRL+F')
        
        if should_create_widget(self.display):
            self.display = QtWidgets.QTextBrowser()
            self.display.setReadOnly(True)
        
        if should_create_widget(self.search):
            self.search = QtWidgets.QLineEdit()
        
        if should_create_widget(self.search_button):
            self.search_button = QtWidgets.QPushButton('Search')
        
        if should_create_widget(self.search_container):
            self.search_container = QtWidgets.QWidget()
        
        if should_create_widget(self.search_box):
            self.search_box = QtWidgets.QWidget()
        
        if should_create_widget(self.search_augment_container):
            self.search_augment_container = QtWidgets.QWidget()
        
        if should_create_widget(self.search_insensitive):
            self.search_insensitive = QtWidgets.QCheckBox('Insensitive?')
        
        if should_create_widget(self.search_whole):
            self.search_whole = QtWidgets.QCheckBox('Whole Word?')
        
        if should_create_widget(self.search_backward):
            self.search_backward = QtWidgets.QCheckBox('Backwards?')
        
        if should_create_widget(self.search_auto):
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
