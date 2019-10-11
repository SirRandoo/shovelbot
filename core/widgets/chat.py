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
import typing

from PyQt5 import QtCore, QtWebEngineWidgets, QtWidgets

from QtUtilities import widgets
from QtUtilities.utils import should_create_widget


class Chat(widgets.QRedockable):
    """A dockable chat widget."""
    
    def __init__(self, *, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(Chat, self).__init__(parent=parent)
        
        # Ui Attributes #
        self.central: typing.Optional[QtWidgets.QMainWindow] = None
        self.layout: typing.Optional[QtWidgets.QVBoxLayout] = None
        self.display: typing.Optional[QtWebEngineWidgets.QWebEngineView] = None
        self.container: typing.Optional[QtWidgets.QWidget] = None
        self.input: typing.Optional[QtWidgets.QLineEdit] = None
        self.send: typing.Optional[QtWidgets.QPushButton] = None
        
        # Internal calls
        self.setup_ui()
        self.topLevelChanged.connect(self.adjust_window)
    
    # Ui Methods #
    def setup_ui(self):
        """Prepares the chatable's UI."""
        if should_create_widget(self.central):
            self.central = QtWidgets.QWidget(flags=QtCore.Qt.Widget)
            self.layout = QtWidgets.QVBoxLayout(self.central)
            self.layout.setContentsMargins(0, 0, 0, 0)
            
            self.setWidget(self.central)
        
        if should_create_widget(self.display):
            self.display = QtWebEngineWidgets.QWebEngineView()
            self.display.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            
            if self.layout.indexOf(self.display) == -1:
                self.layout.addWidget(self.display)
        
        if should_create_widget(self.container):
            self.container = QtWidgets.QWidget(flags=QtCore.Qt.Widget)
            self.container.setLayout(QtWidgets.QHBoxLayout())
            self.layout.addWidget(self.container)
            
            self.container.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        
        if should_create_widget(self.input):
            self.input = QtWidgets.QLineEdit()
            
            if self.container.layout().indexOf(self.input) == -1:
                self.container.layout().addWidget(self.input)
        
        if should_create_widget(self.send):
            self.send = QtWidgets.QPushButton("Send")
            
            if self.container.layout().indexOf(self.send) == -1:
                self.container.layout().addWidget(self.send)
    
    # Slots
    def adjust_window(self, floating: bool):
        """A hacky way to make the widget visible to OBS."""
        if floating:
            self.setWindowTitle('Chat')
            self.setWindowFlags(QtCore.Qt.Window)
            self.show()
        
        else:
            self.setWindowTitle('')
            self.setWindowFlags(QtCore.Qt.Widget)
