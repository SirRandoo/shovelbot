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

from PySide6 import QtCore, QtGui, QtWebEngineWidgets, QtWidgets


class Info(QtWidgets.QDialog):
    """A dialog for displaying complex information to the user."""
    logger = logging.getLogger("core.info")

    positive_action = QtCore.Signal()
    negative_action = QtCore.Signal()

    def __init__(self, *, parent: QtWidgets.QWidget = None):
        super(Info, self).__init__(parent=parent)

        self._stack = QtWidgets.QStackedWidget(parent=self)
        self._text_display = QtWidgets.QTextBrowser(parent=self)
        self._web_display = QtWebEngineWidgets.QWebEngineView(parent=self)

        self._button_container = QtWidgets.QWidget(parent=self)
        self._positive_button = QtWidgets.QPushButton("OK", self._button_container)
        self._negative_button = QtWidgets.QPushButton("Cancel", self._button_container)

        self._quitting = False

        self.setLayout(QtWidgets.QVBoxLayout())
        self.layout().addWidget(self._stack)
        self.layout().addWidget(self._button_container)

        self._button_container.setLayout(QtWidgets.QHBoxLayout())
        self._button_container.layout().addSpacerItem(QtWidgets.QSpacerItem(-1, -1))
        self._button_container.layout().insertWidget(1, self._positive_button)
        self._button_container.layout().insertWidget(2, self._negative_button)

        self._stack.addWidget(self._web_display)
        self._stack.addWidget(self._text_display)

        self._positive_button.clicked.connect(self.hide)
        self._positive_button.clicked.connect(self.positive_action.emit)

        self._negative_button.clicked.connect(self.hide)
        self._negative_button.clicked.connect(self.negative_action.emit)

        self._button_container.setHidden(True)
        self._button_container.layout().setContentsMargins(5, 5, 5, 5)

    def show_buttons(self):
        """Shows the button widget."""
        self._button_container.setVisible(True)

    def set_buttons(self, *, positive: str = None, negative: str = None):
        """Sets the display text for the buttons."""
        if positive is not None:
            self._positive_button.set_text(positive)
            self._positive_button.show()

        else:
            self._positive_button.hide()

        if negative is not None:
            self._negative_button.set_text(negative)
            self._negative_button.show()

        else:
            self._negative_button.hide()

    def set_text(self, content: str):
        """Sets the text that will be displayed in the QTextBrowser."""
        self._text_display.set_text(content)

    def set_html(self, content: str):
        """Sets the HTML that will be displayed in the QWebEngineView."""
        self._web_display.setHtml(content)

    def show_text(self, content: str, *, with_buttons: bool = False):
        """A convenience method for setting the text in the QTextBrowser, then showing that browser."""
        self.set_text(content)
        self.show()

        if with_buttons:
            self._button_container.setVisible(True)

        else:
            self._button_container.setHidden(True)

    def show_html(self, content: str, *, with_buttons: bool = False):
        """A convenience method for setting the text in the QWebEngineView, then showing that view."""
        self.set_html(content)
        self.show()

        if with_buttons:
            self._button_container.setVisible(True)

        else:
            self._button_container.setHidden(True)

    def quit(self):
        """A convenience method for properly closing the dialog."""
        self._quitting = True
        self.close()

    def closeEvent(self, event: QtGui.QCloseEvent):
        if self._quitting:
            event.accept()

        else:
            event.ignore()
            self.hide()
