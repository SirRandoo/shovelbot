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
import logging
from urllib import parse as url_parse

from PyQt5 import QtGui, QtWidgets

from QtUtilities import requests
from .enums import ApiTypes


# noinspection PyArgumentList
class Dialog(QtWidgets.QDialog):
    """A dialog primarily used for checking, displaying, and handling updates."""
    
    def __init__(self, **kwargs):
        # Super Call #
        super(Dialog, self).__init__(parent=kwargs.get('parent'))
        
        # "Public" Attributes #
        self.api_type: ApiTypes = kwargs.get('api_type')
        
        # "Private" Attributes #
        self._factory: requests.Factory = kwargs.get('factory')
        self._logger = logging.getLogger('core.updater')
        
        # "Internal" Attributes #
        self._force_quit: bool = False
    
    # Api Methods #
    def check_github(self):
        """Checks for new releases on GitHub."""
        app = QtWidgets.QApplication.instance()
        
        if app is not None:
            repo = url_parse.urlencode(app.applicationName(), safe='')
            owner = url_parse.urlencode(app.organizationName(), safe='')
            
            r = self._factory.get(f'https://api.github.com/repos/{owner}/{repo}/releases')
            
            if r.is_ok():
                data = r.json()
                
                try:
                    latest = data[0]
                
                except IndexError:
                    pass
            
            else:
                self._logger.warning('Could not check for updates!')
                self._logger.warning(f'Reason: {r.error_string()}')
        
        else:
            self._logger.warning('QApplication is not initialized!')
    
    # Overrides #
    def closeEvent(self, event: QtGui.QCloseEvent):
        """An overrides to Qt's closeEvent for stopping the update."""
        if self._force_quit:
            event.accept()
            return
