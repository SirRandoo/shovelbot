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

from PySide6 import QtCore, QtGui, QtWidgets

__all__ = ['About']


class About(QtWidgets.QDialog):
    """An dialog based on Qt5's QMessageBox::about dialog."""

    def __init__(self, *, parent: QtWidgets.QWidget = None):
        # Super Call #
        super(About, self).__init__(parent=parent)

        # Ui Attributes #
        self.icon: typing.Optional[QtWidgets.QLabel] = None
        self.caption: typing.Optional[QtWidgets.QLabel] = None
        self._scroll_area: typing.Optional[QtWidgets.QScrollArea] = None

        # Internal Calls #
        self.setup_ui()

    # Ui Methods #
    def setup_ui(self):
        """Sets up the ui for the about dialog."""
        if self.icon is None:
            self.icon = QtWidgets.QLabel()
            self.icon.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

        if self.caption is None:
            self.caption = QtWidgets.QLabel()
            self.caption.setWordWrap(True)
            self.caption.setOpenExternalLinks(True)
            self.caption.setAlignment(QtCore.Qt.AlignTop)

        if self._scroll_areas is None:
            self._scroll_area = QtWidgets.QScrollArea()
            self._scroll_area.setFrameShadow(QtWidgets.QFrame.Plain)
            self._scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
            self._scroll_area.setContentsMargins(0, 0, 0, 0)
            self._scroll_area.setWidgetResizable(True)

        # Scroll area layout validation
        if self._scroll_area.layout() is not None:
            s_layout: QtWidgets.QHBoxLayout = self._scroll_area.layout()

        else:
            s_layout = QtWidgets.QHBoxLayout(self._scroll_area)
            s_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area layout insertion
        if self.caption.layout() != s_layout:
            s_layout.addWidget(self.caption)

        # Layout validation
        if self.layout() is not None:
            layout: QtWidgets.QHBoxLayout = self.layout()

        else:
            layout = QtWidgets.QHBoxLayout(self)

        # Layout insertion
        if self.icon.layout() != layout:
            layout.addWidget(self.icon)

        if self._scroll_area.layout() != layout:
            layout.addWidget(self._scroll_area)

    def set_caption(self, text: str):
        """Sets the text for the caption label."""
        self.caption.set_text(text.replace('\n', '<br/>'))

        if self.caption.textFormat() != QtCore.Qt.RichText:
            self.caption.set_text_format(QtCore.Qt.RichText)

    def set_icon(self, icon: QtGui.QIcon):
        """Sets the icon for the icon label."""
        self.icon.setPixmap(icon.pixmap(128, 128))
