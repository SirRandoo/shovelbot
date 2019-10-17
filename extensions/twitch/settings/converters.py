# This file is part of Twitch for ShovelBot.
#
# Twitch for ShovelBot is free software:
# you can redistribute it
# and/or modify it under the
# terms of the GNU General
# Public License as published by
# the Free Software Foundation,
# either version 3 of the License,
# or (at your option) any later
# version.
#
# Twitch for ShovelBot is distributed in
# the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without
# even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the
# GNU General Public License along with
# Twitch for ShovelBot.  If not,
# see <https://www.gnu.org/licenses/>.
from PyQt5 import QtCore, QtWidgets

from QtUtilities import settings, signals
from widgets import ShovelBot
from .generator import Generator


def token(obj: settings.Setting):
    # TODO: Currently, if the user enters a third-party token, the converter
    #       won't store it in the same manner it would if one were generated.
    
    # Imports
    from ..dataclasses import Token
    
    # Declarations
    container = QtWidgets.QWidget()
    layout = QtWidgets.QHBoxLayout(container)
    display = QtWidgets.QLineEdit(parent=container)
    generate = QtWidgets.QToolButton(parent=container)
    
    # If the widget is a top-level window, hide it.
    if container.isWindow():
        container.hide()
    
    # Update the widgets' visuals.
    generate.setText('↻')
    display.setEchoMode(display.PasswordEchoOnEdit)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Ensure the current value is displayed, if there is one.
    if obj.value is not None:
        display.setText(str(obj.value))
    
    # Forcibly reassign the converter
    obj.converter = 'twitch.token'
    
    # Signals
    def on_generate(t: Token):
        """Invoked when the user completes the OAuth flow.  This method is
        responsible for updating the QLineEdit and Setting objects to represent
        the freshly generated token."""
        obj.set_value(t.token)
        display.setText(t.token)
        obj.data['scopes'] = [s.value for s in t.scopes]
        
        display.setToolTip('Current scopes: {}'.format(', '.join(obj.data['scopes'])))
    
    def generate_token():
        """Invoked when the user clicks the generate QToolButton.  This method
        is responsible for displaying the OAuth flow to the user in, hopefully,
        a user friendly way."""
        client: ShovelBot = QtWidgets.QApplication.instance().client
        g = Generator(parent=client.settings)
        g.setWindowFlags(QtCore.Qt.Dialog | QtCore.Qt.WindowSystemMenuHint)
        
        g.setup_ui()
        
        g.GENERATED.connect(on_generate)
        
        g.show()
        g.adjustSize()
        
        signals.wait_for_signal_or(g.accepted, g.rejected)
        g.deleteLater()
    
    # Connect the widget's signals to their respective slots.
    generate.clicked.connect(generate_token)
    
    # Layout insertion
    layout.addWidget(display)
    layout.addWidget(generate)
    
    # Return value
    return container
