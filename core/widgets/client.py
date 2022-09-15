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
import functools
import importlib
import inspect
import json
import logging
import pathlib
import textwrap
import typing
from typing import List

import PySide6
import sys
from PySide6 import QtCore, QtGui, QtHelp, QtNetwork, QtSql, QtWidgets

from QtUtilities import requests, settings, signals, themes
from QtUtilities.widgets import progress
from core import commands, dataclassez
from .about import About
from .help import Help
from .uis.client import Client as ClientUi

__all__ = ['Client']


class Client(QtWidgets.QMainWindow):
    LOGGER = logging.getLogger('core')

    REPOSITORY = QtCore.QUrl('https://github.com/sirrandoo/shovelbot')
    RESOURCES = QtCore.QDir('resources')
    ASSETS = QtCore.QDir(RESOURCES.filePath('assets'))
    AUTHORS = {'SirRandoo'}
    LICENSE = 'GNU General Public License 3 or later'
    LICENSE_URL = QtCore.QUrl('https://www.gnu.org/licenses/quick-guide-gplv3.html')

    aboutToStart = QtCore.Signal()
    aboutToHalt = QtCore.Signal()
    aboutToStop = QtCore.Signal()

    started = QtCore.Signal()
    halted = QtCore.Signal()
    stopped = QtCore.Signal()

    onCommandExecuteRequested = QtCore.Signal(object)
    onCommandExecute = QtCore.Signal(object)
    denyCommandExecute = QtCore.Signal(object)

    def __init__(self):
        # Super call
        super(Client, self).__init__()

        # "Public" declarations
        self.ui = ClientUi()
        self.help_dialog = None
        self.request_factory = None
        self.extensions = {}
        self.settings = settings.Display()
        self.themes = [themes.dark, themes.high_contrast]
        self.display_timer = QtCore.QTimer(parent=self)
        self.base_theme = QtGui.QPalette(self.palette())
        self.help_engine = QtHelp.QHelpEngineCore('resources/docs/shovelbot.qhc')
        self.command_manager = commands.Manager()
        self.database = QtSql.QSqlDatabase.addDatabase('QSQLITE')

        # "Private" attributes
        self._settings_file = None

        # Internal calls
        self.help_engine.warning.connect(self.LOGGER.warning)

        self.database.setDatabaseName('data/shovelbot.db')

    # Ui methods
    def setup(self):
        """Performs set up tasks."""
        app = QtWidgets.QApplication.instance()
        self.request_factory = requests.Factory(manager=app.network_access_manager)

        with progress.Context() as p:
            p.task('Loading settings...', self.load_settings)
            p.task('Preparing ui...', self.ui.setup, parent=self)
            p.task('Preparing help ui...', self.setup_help_ui)
            p.task('Stitching ui signals...', self.ui.stitch)
            p.task('Stitching settings to slots...', self.stitch_settings)
            p.task('Applying settings...', self.apply_settings)
            p.task('Loading extensions...', self.load_extensions)
            p.task('Setting up extensions...', self.setup_extensions)
            p.wait_for_task('Preparing help files...', self.help_engine.setupFinished,
                            before=self.help_engine.setupData)

            p.finished.connect(self.show)
            p.finished.connect(self.dump)

    def setup_help_ui(self):
        """Prepares the help UI for display."""
        if self.help_dialog is None:
            self.help_dialog = Help(engine=self.help_engine)

    # Settings methods
    def load_settings(self):
        """Loads ShovelBot's settings."""
        if self._settings_file is None:
            app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
            self._settings_file = QtCore.QFile(f'{app.applicationName()}.settings')

        if self._settings_file.exists():
            if not self._settings_file.isOpen():
                self._settings_file.open(self._settings_file.ReadOnly | self._settings_file.Text)

            if self._settings_file.isReadable():
                raw_text: QtCore.QByteArray = self._settings_file.readAll()

                if not raw_text.isNull():
                    raw_text: str = raw_text.data().decode()

                    try:
                        decoded_text = json.loads(raw_text)

                    except ValueError as e:
                        self.LOGGER.warning('Could not decode file settings.json!')
                        self.LOGGER.warning(f'Exception Type: {e.__class__.__name__}')
                        self.LOGGER.warning(f'Exception Cause: {e.__cause__}')

                    else:
                        for raw_setting in decoded_text:
                            try:
                                setting = settings.Setting.from_data(raw_setting)

                            except ValueError as e:
                                self.LOGGER.warning('Could not decode file settings.json!')
                                self.LOGGER.warning(f'Exception Type: {e.__class__.__name__}')
                                self.LOGGER.warning(f'Exception Cause: {e.__cause__}')

                            else:
                                if self.settings is None:
                                    self.settings = settings.Display()

                                self.settings.register_setting(setting)

                    finally:
                        if self._settings_file.isOpen():
                            self._settings_file.close()

                        self.validate_settings()

                else:
                    self.LOGGER.warning('Settings file contains no data!')
                    self.LOGGER.warning('Was this an error?')

                    for s in self.generate_settings():
                        self.settings.register_setting(s)

        else:
            self.LOGGER.warning('Settings file does not exist!')
            self.LOGGER.info('Is this a first run?')

            for s in self.generate_settings():
                self.settings.register_setting(s)

    def generate_settings(self) -> List[settings.Setting]:
        """Generates a blank config for ShovelBot."""
        # Top-Level settings
        top = {
            'appearance': settings.Setting('appearance', tooltip='Settings related the visual display of the client.'),
            'extensions': settings.Setting('extensions', tooltip='Settings related to the extension framework.'),
            'system': settings.Setting('system', tooltip='Settings related to ShovelBot as a whole.')
        }

        # appearance settings
        top['appearance'].add_children(
            settings.Setting('theme', 0, converter='qcombobox',
                             data={
                                 'choices': ['Light'] + [t.__name__.replace('_', ' ').title()
                                                         for t in self.themes]
                             },
                             tooltip='The overall theme of the application as a whole.  '
                                     'Extensions should add support for this option.'),

            settings.Setting('stream', tooltip='Settings related to the stream settings.')
        )

        # appearance.stream settings
        top['appearance']['stream'].add_children(
            settings.Setting('sync', True, tooltip='Automatically sync stream metadata across all platforms.')
        )

        # extensions settings
        top['extensions'].add_children(
            settings.Setting('platforms', tooltip='Settings related to platform extensions.'),

            settings.Setting('directory', 'extensions', display_name='Extensions Directory',
                             tooltip='The directory extensions are contained in.'
                                     '\n'
                                     'The directory cannot contain...'
                                     '<ul>'
                                     '<li>symbols</li>'
                                     '<li>start with a number</li>'
                                     '<li>contain spaces</li>'
                                     '</ul>', converter='qdir'),
            settings.Setting('auto_start', False, display_name='Start on Startup',
                             tooltip='Whether or not the bot will simulate a user pressing "Start ShovelBot" when the '
                                     'client finishes its startup tasks.'),
            settings.Setting('auto_load', True, display_name='Load Extensions on Startup',
                             tooltip='Whether or not the bot will automatically load all extensions in the specified '
                                     'directory.  If this is unchecked, extensions will have to be manually loaded in '
                                     'the extensions panel.')
        )

        # extensions.platforms settings

        # system settings
        top['system'].add_children(
            settings.Setting('debug', False, display_name='Debug Mode?',
                             tooltip='Whether or not ShovelBot is in debug mode.'),
            settings.Setting('prefix', '!',
                             tooltip='The prefix to use for system (built-in) commands.',
                             display_name='System Prefix'),

            settings.Setting('updates', None, display_name='Updates',
                             tooltip='Settings related to the update checker.'),

            settings.Setting('window', tooltip='Settings related to the literal window of ShovelBot.', hidden=True)
        )

        # system.updates settings
        top['system']['updates'].add_children(
            settings.Setting('channel', 0, display_name='Release channel',
                             tooltip='The type of releases to update to.',
                             converter='qcombobox', data={'choices': ['Release', 'Beta']}),
            settings.Setting('auto', True, display_name='Automatic update checks?',
                             tooltip='Whether or not ShovelBot will automatically check for updates on startup.')
        )

        # settings.window settings
        top['system']['window'].add_children(
            settings.Setting('x', self.x(), display_name='Window X', read_only=True,
                             tooltip='The top-left position the main window will be along the X axis.'),
            settings.Setting('y', self.y(), display_name='Window Y', read_only=True,
                             tooltip='The top-left position the main window will be along the Y axis.'),
            settings.Setting('width', self.width(), display_name='Window Width', read_only=True,
                             tooltip='The width of the main window.'),
            settings.Setting('height', self.height(), display_name='Window Height', read_only=True,
                             tooltip='The height of the main window.')
        )

        # Returning
        return list(top.values())

    def validate_settings(self):
        """Validates a config for ShovelBot."""

    def stitch_settings(self):
        """Stitches settings to their respective slots."""
        self.settings['appearance']['theme'].value_changed.connect(self.ui.apply_theme)

    def apply_settings(self):
        """Applies settings to ShovelBot.  This method is responsible for
        applying settings, like theme changes, to the display."""
        # Display
        self.move(self.settings['system']['window']['x'].value, self.settings['system']['window']['y'].value)
        self.resize(self.settings['system']['window']['width'].value, self.settings['system']['window']['height'].value)
        self.ui.apply_theme()

        # Update checker
        if self.settings['system']['updates']['auto'].value:
            # noinspection PyCallByClass,PyTypeChecker
            QtCore.QTimer.singleShot(1, functools.partial(self.update_check, automatic=True))

        # Extensions
        if self.settings['extensions']['auto_start'].value:
            self.ui.start_action.trigger()

    # Extension methods
    def load_extensions(self):
        """Loads all extensions in the specified extensions directory."""
        # Declarations
        path: str = self.settings['extensions']['directory'].value
        directory = pathlib.Path(path)

        # Directory validation
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)

        for path in directory.iterdir():  # type: pathlib.Path
            if path.name.startswith('_'):
                self.LOGGER.debug(f'Skipping {path!s}...')
                continue

            self.LOGGER.info(f'Attempting to load extension @ {path!s}')

            try:
                extensions = self.load_extension(path)

            except ModuleNotFoundError:
                self.LOGGER.warning(f'Cannot load a non-existent extension @ {path!s}!')

            except ImportError as e:
                self.LOGGER.warning(f'Could not load extension @ {path!s}!  Reason: {e!s}')

            except LookupError:
                self.LOGGER.warning(f'Extension @ {path!s} does not contain an Extension subclass!')

            else:
                for extension in extensions:
                    self.ui.extensions_table.append(extension.DISPLAY_NAME, extension.VERSION.toString(),
                                                    extension.STATE.name.replace('_', ' ').capitalize())
                    self.ui.extensions_table.set_row_header(self.ui.extensions_table.rowCount() - 1, extension.NAME)
                    self.ui.extensions_table.resizeColumnsToContents()

                    self.extensions[extension.NAME] = extension

    def setup_extensions(self):
        """Sets up all loaded extensions."""
        self.LOGGER.info(f'Setting up {len(self.extensions)} extensions...')

        for ext in self.extensions.values():
            if isinstance(ext, dataclassez.ExtensionStub):
                continue  # Since we can't set up a stub

            self.LOGGER.debug(f'Setting up {ext.DISPLAY_NAME}...')

            try:
                ext.setup()

            except NotImplementedError:
                self.LOGGER.debug(f'{ext.DISPLAY_NAME} does not implement a setup method!')

            else:
                self.LOGGER.debug(f'{ext.DISPLAY_NAME} was successfully set up!')

            finally:
                try:
                    row, header = self.ui.extensions_table.row_from_header(ext.NAME)

                except LookupError:
                    self.LOGGER.warning(f'Could not update display for extension "{ext.NAME}"!')

                else:
                    self.ui.extensions_table.set_row(row, State=ext.STATE.name.replace('_', ' ').capitalize())

    def teardown_extensions(self):
        """Tears down all loaded extensions."""
        self.LOGGER.warning(f'Tearing down {len(self.extensions)} extensions...')

        for ext in self.extensions.values():
            if isinstance(ext, dataclassez.ExtensionStub):
                continue  # Since we can't tear down a stub

            self.LOGGER.debug(f'Tearing down {ext.DISPLAY_NAME}...')

            try:
                ext.teardown()

            except NotImplementedError:
                self.LOGGER.debug(f'{ext.DISPLAY_NAME} does not implement a teardown method!')

            else:
                self.LOGGER.debug(f'{ext.DISPLAY_NAME} was successfully torn down!')

            finally:
                try:
                    row, header = self.ui.extensions_table.row_from_header(ext.NAME)

                except LookupError:
                    self.LOGGER.warning(f'Could not update display for extension "{ext.NAME}"!')

                else:
                    self.ui.extensions_table.set_row(row, State=ext.STATE.name.replace('_', ' ').capitalize())

    def unload_extensions(self):
        """Unloads all extensions."""
        self.LOGGER.warning(f'Unloading {len(self.extensions)} extensions...')

        for name, value in self.extensions.copy().items():
            if isinstance(value, dataclassez.ExtensionStub):
                continue  # Since we can't unload a stub

            try:
                stub = value.unload()

            except NotImplementedError:
                self.LOGGER.debug(f'{value.DISPLAY_NAME} does not implement an unload method!')

            else:
                self.LOGGER.debug(f'{value.DISPLAY_NAME} successfully unloaded!')
                self.extensions[name] = stub

            finally:
                self.LOGGER.info(f'Unregistering commands for {value.DISPLAY_NAME}...')
                before = len(self.command_manager.commands)

                for attr, inst in inspect.getmembers(value):
                    if isinstance(inst, commands.Command):
                        try:
                            self.command_manager.commands.remove(inst)

                        except ValueError:
                            self.LOGGER.warning(f'Command {value.__class__.__name__}.{inst.name} was not previously '
                                                f'registered!')

                        else:
                            self.LOGGER.debug(f'Unregistered command {value.__class__.__name__}.{inst.name}!')

                self.LOGGER.info(f'Unregistered {before - len(self.command_manager.commands)} commands!')

                try:
                    row, *_ = self.ui.extensions_table.row_from_header(value.NAME)

                except LookupError:
                    self.LOGGER.debug(f"Couldn't remove {value.DISPLAY_NAME} from the extensions table!")
                    self.LOGGER.debug(
                        'Extensions table: {}'.format('DELETED' if self.ui.extensions_table is None else 'EXISTS')
                    )
                    self.LOGGER.debug('Extension: {}'.format(self.extensions[value.NAME].STATE.value))
                    self.LOGGER.debug('Row: probably deleted by an extension')

                else:
                    self.ui.extensions_table.set_row(row, State=value.STATE.name.replace('_', ' ').capitalize())

        self.LOGGER.warning(f'Unloaded {len(self.extensions)} extensions!')
        self.extensions.clear()

    def load_extension(self, path: pathlib.Path) -> typing.List[dataclassez.Extension]:
        """Loads an extension in the specified directory."""
        # Existence check
        if not path.exists():
            raise ModuleNotFoundError

        # Declarations
        prior = list(sys.modules.keys())
        import_path = '.'.join(path.parts).rstrip('.py')
        logger = logging.getLogger(f'{self.LOGGER.name}.loader')
        extensions = []

        # Loading sequence
        logger.info(f'Loading extensions @ {path!s}...')

        try:
            p = importlib.import_module(import_path)

        except ImportError as e:
            logger.warning(f'Extension loading failed!  Reason: {e!s}')

            logger.warning(f'Attempting to clean up environment...')
            for key, value in sys.modules.copy().items():
                if key not in prior and not inspect.isbuiltin(value) and key not in sys.builtin_module_names:
                    logger.debug(f'Removing {key} from loading modules...')
                    del sys.modules[key]

            raise ImportError from e

        else:
            logger.info('Extension imported!')
            query = []

            try:
                for attr in p.__all__:
                    inst = getattr(p, attr)

                    if not inspect.isclass(inst):
                        continue

                    query.append((attr, inst))

            except AttributeError:
                logger.debug(f'Extension does not define __all__!')
                logger.debug(f'Falling back to inspect.getmembers...')

                query = [(n, i) for n, i in inspect.getmembers(p) if inspect.isclass(i)]

            # Dump the namespace
            self.dump_extension_namespace(prior, list(sys.modules.keys()))

            # Scan the module for an Extension class
            logger.info('Searching for Extension class...')
            for attr, inst in query:
                # Dump the current classes inheritance list
                self.dump_extension_inheritance(inst)

                # Ensure we don't reload already loaded extensions
                if any([isinstance(e, inst) for e in self.extensions]):
                    continue

                # Check to see if an inherited class is the Extension class
                if any([c == dataclassez.Extension for c in inspect.getmro(inst)]):
                    logger.debug(f'Found class {attr}!  Creating a new instance...')
                    instance: dataclassez.Extension = inst()

                    instance.__package = import_path
                    setattr(instance, f'_{attr}__package', import_path)
                    setattr(instance, f'_{attr}__path', path)

                    logger.debug(f'Storing imported modules to {attr}.__imports...')
                    setattr(instance, f'_{attr}__imports', [key for key in sys.modules.copy() if key not in prior])
                    logger.debug(f'Stored {len(getattr(instance, f"_{attr}__imports", []))} values.')

                    if isinstance(instance, dataclassez.Platform):
                        logger.debug(f"Binding platform {instance.DISPLAY_NAME}'s signals...")

                        logger.debug(f'Binding {inst}.onMessage to {self.__class__.__name__}.'
                                     f'{self.process_chat_message.__name__}...')
                        instance.onMessage.connect(lambda x, i = instance: self.process_chat_message(i, x))

                        logger.debug(f"Bound platform {instance.DISPLAY_NAME}'s signals.")

                    logger.debug(f'Storing extension "{instance.DISPLAY_NAME}"')
                    extensions.append(instance)

            if extensions:
                logger.info('Adding extension commands...')
                logger.info('Indexing extension(s) for commands...')

                for extension in extensions:
                    logger.info(f'Indexing extension "{extension.NAME}"...')
                    temp = []

                    for attr, inst in inspect.getmembers(extension):
                        if isinstance(inst, commands.Command):
                            logger.debug(f'Found {extension.__class__.__name__}.{attr}#{inst.__class__.__name__}')

                            temp.append(inst)

                    logger.info(f'Found {len(temp)} commands!')
                    self.command_manager.commands.extend(temp)

                    logger.debug('{} objects, {} commands, and {} groups'.format(
                        len(temp),
                        sum([1 for c in temp if isinstance(c, commands.Command) and not isinstance(c, commands.Group)]),
                        sum([1 for c in temp if isinstance(c, commands.Group)])
                    ))

                return extensions

            raise LookupError(f"Extension @ {import_path} doesn't have an Extension class!")

    def load_from_stub(self, stub: dataclassez.ExtensionStub) -> typing.List[dataclassez.Extension]:
        """Loads an extension from an extension stub."""
        # Instance validation
        if not isinstance(stub, dataclassez.ExtensionStub):
            raise ValueError(f'Expected ExtensionStub;  received Extension!')

        # Load extension
        self.LOGGER.info(f'Attempting to load extension @ {stub.PATH!s}')

        try:
            ext = self.load_extension(stub.PATH)

        except ModuleNotFoundError:
            self.LOGGER.warning(f'Cannot load a non-existent extension @ {stub.PATH!s}!')

        except ImportError as e:
            self.LOGGER.warning(f'Could not load extension @ {stub.PATH!s}!  Reason: {e!s}')

        except LookupError:
            self.LOGGER.warning(f'Extension @ {stub.PATH!s} does not contain an Extension subclass!')

        else:
            return ext

    # Chat methods
    def process_chat_message(self, platform: dataclassez.Platform, message: dataclassez.Message):
        """Processes a raw chat message into a command."""
        if not message.content.startswith(self.settings['system']['prefix'].value):
            if self.command_manager.PARSER_DEBUG:
                self.LOGGER.debug(f'Message "{message}" '
                                  f'does not start with the user\'s '
                                  f'requested prefix of '
                                  f'"{self.settings["extensions"]["platforms"]["command_prefix"].value}"!')

            return

        command, arguments = self.command_manager.parse(message.content, ignore_case=True)

        if command is not None:
            if self.command_manager.PARSER_DEBUG:
                self.LOGGER.debug(f'Located command "{command.qualified_name}"!')

            # Re-implement commands.Manager to tie into the signals defined above.
            argspec = inspect.getfullargspec(command.func)
            key_arguments = {}

            for argument in arguments.copy():
                if '=' in argument and self.command_manager.is_kv_pair(argument):
                    k, v = argument.split('=')
                    key_arguments[k] = v if v else None

                    arguments.pop(arguments.index(argument))

            args, originals = self.command_manager.convert_args(command.func, *arguments, **key_arguments)

            if not argspec.varargs:
                final_positionals = []

                for key, value in originals.items():
                    if key not in args:
                        final_positionals.append(value)

            else:
                final_positionals = arguments

            # Build a context object
            try:
                # noinspection PyUnresolvedReferences
                prefix = command.prefix

            except AttributeError:
                prefix = self.settings['system']['prefix'].value

            context = commands.Context(
                prefix=prefix,
                message=message,
                platform=platform,
                command=command,
                arguments=final_positionals,
                kwarguments=args
            )

            # Inform listeners that a command is about to be executed
            self.onCommandExecuteRequested.emit(context)

            emitted, returnable = signals.wait_for_signal(self.denyCommandExecute, timeout=5)

            if emitted:
                returnable: typing.Union[commands.Command, commands.Group]

                if returnable == context:
                    return self.LOGGER.debug(f'Command execution of "{command.qualified_name}" was denied!')

            else:
                try:
                    command(*final_positionals, **args)

                except commands.errors.CommandsError:
                    self.LOGGER.warning(f'Command "{command.qualified_name}" does not contain a callable!')

                else:
                    self.onCommandExecute.emit(context)

    # File menu slots
    def start_bot(self):
        """Starts ShovelBot.

        When ShovelBot starts, all extensions that listen to `aboutToStart` or
        `started` are expected to call their starting procedures.  If your
        extension allows ShovelBot to connect to a streaming platform, you
        should generally attach your connection logic to one of those signals."""
        self.LOGGER.info('Performing starting operations...')
        self.aboutToStart.emit()
        self.started.emit()

        self.LOGGER.info('ShovelBot started!')

    def halt_bot(self):
        """Halts ShovelBot.

        When ShovelBot halts, all extension that listen to `aboutToHalt` or `
        halted` are expected to call their halting procedures.

        When ShovelBot is "halted" the bot should maintain connections to
        streaming platforms, but all functionality is lost.  If an extension
        contains commands, only critical commands should be invoked.

        - Halt support is optional"""
        self.LOGGER.warning('Performing halt operations...')
        self.aboutToHalt.emit()
        self.halted.emit()

        self.LOGGER.warning('ShovelBot halted!')

    def stop_bot(self):
        """Stops ShovelBot.

        When ShovelBot stops, all extensions that listen to `aboutToStop` or
        `stopped` are expected to call their stopping procedures.

        When ShovelBot is "stopped" the bot should close all connections to
        streaming platforms."""
        self.LOGGER.warning('Performing stopping operations...')
        self.aboutToStop.emit()
        self.stopped.emit()

        self.LOGGER.warning('ShovelBot stopped!')

    # Help menu slots
    def help(self):  # TODO: Fix the help dialog
        """Displays the help dialog for ShovelBot."""
        index: QtCore.QUrl = self.help_engine.findFile(
            QtCore.QUrl(f'qthelp://{self.help_engine.registeredDocumentations()[-1]}/docs/index.html')
        )

        # Check to see if the index file exists
        if not index.isValid():
            self.LOGGER.warning('No help documentation could be found!')

            self.help_dialog.display.setHtml(
                '<h3>Help documentation is missing!</h3>'
                '<p>'
                '   You should...'
                '   <ol>'
                '       <li>Reinstall ShovelBot</li>'
                f'      <li>Submit a bug report <a href="{self.REPOSITORY.toDisplayString()}/issues/new">here</a></li>'
                '   </ol>'
                '</p>'
            )
            return self.help_dialog.show()

        # Read the contents of the file
        file_data: QtCore.QByteArray = self.help_engine.fileData(index)

        # Set the display's contents to the index's
        self.help_dialog.display.setHtml(file_data.data().decode())

        # Show the dialog
        self.help_dialog.show()

    def about(self):
        """Displays the about dialog for ShovelBot."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        dialog = About()

        # Metadata
        dialog.set_icon(self.windowIcon())
        # noinspection PyCallingNonCallable
        dialog.set_caption(textwrap.dedent(f"""
            <p style="padding:0; margin-bottom:0;">
                <div align="center" style="font-weight: bold; padding: 0; font-size: large; margin: 0;">
                    {self.__doc__}
                </div>

                <div align="center" style="font-style: italic; padding: 0; font-size: medium; margin: 0;">
                    Created by {", ".join(self.AUTHORS)}
                </div>

                <hr width="100%" style="padding: 0; margin-bottom: 0;"/><br/>
            </p>
            
            <p style="padding: 0; margin-top: 0; margin-bottom: 0;">
                This software is licensed under <a href="{self.LICENSE_URL.toDisplayString()}">{self.LICENSE}</a>.
                You're free to modify or redistribute it under the conditions of these license.  The source code
                can be found at its <a href="{self.REPOSITORY.toDisplayString()}">repository</a>.<br/>
                <br/>
                <br/>
                Version: <a href="{self.REPOSITORY.toDisplayString()}/releases/tag/v{app.applicationVersion()}">
                    {app.applicationVersion()}
                </a><br/>
                Qt Version: <a href="https://www.qt.io/">{PySide6.__version__}</a><br/>
                PyQt5 Version: <a href="https://www.riverbankcomputing.com/software/pyqt/download5">
                    {PySide6.__version__}
                </a>
            </p>
        """).replace('\n', ''))

        # Execution
        dialog.show()
        signals.wait_for_signal_or(dialog.accepted, dialog.rejected)

    def update_check(self, *, automatic: bool = None):
        """Checks for client updates and extension updates."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()

        # Updater state check
        if app.disable_updater:
            return self.statusBar().showMessage('Updater disabled!', 3 * 1000)

        # noinspection PyCallingNonCallable
        version, _ = QtCore.QVersionNumber.fromString(app.applicationVersion())
        stable: bool = not bool(self.settings['system']['updates']['channel'].value)
        owner, repository, *_ = self.REPOSITORY.path().lstrip('/').split('/')

        # Validation
        if self.request_factory is None:
            self.request_factory = requests.Factory(manager=app.network_access_manager)

        if self.REPOSITORY.host() != 'github.com':
            return self.LOGGER.warning(f'The repository for this application is unsupported.  Please go to '
                                       f'{self.REPOSITORY.toDisplayString()} for new releases.')

        # Request sequence
        self.LOGGER.info('Checking for updates...')
        response = self.request_factory.get(f'https://api.github.com/repos/{owner}/{repository}/releases',
                                            headers={'Accept': 'application/vnd.github.v3+json'})

        # More validation
        if not response.is_okay():
            self.LOGGER.warning(f"Couldn't check for updates!  Reason: {response.error_string()}")

            if response.code() == QtNetwork.QNetworkReply.ContentAccessDenied:
                self.LOGGER.warning('If the repository for this application is private, you cannot use the built-in '
                                    'updater in its current state.')
                self.LOGGER.warning("If you've launch the update checker too often, you may have to wait an hour "
                                    "before you can check for updates.")

                return

        # Serialization
        try:
            data = response.json()

        except ValueError:
            self.LOGGER.debug(f'Received a malformed response from {response.host}!')
            self.LOGGER.warning(f'If {response.host} changed their API recently, you may have to manually update.')

        else:
            if not data:
                self.LOGGER.info('There are no releases yet!')
                return self.statusBar().showMessage('There are no releases yet!', 5 * 1000)

            for release in data:  # type: dict
                is_pre: bool = release.get('prerelease', False)
                release_version, _ = QtCore.QVersionNumber.fromString(release['tag_name'].lstrip('v'))

                # TODO: Update the client if there's a new update
                if (is_pre and not stable) and release_version > version:
                    break

                elif release_version > version:
                    break

                else:
                    return

        # Check for extension updates
        # TODO: Allow extensions to check for updates

        # Inform the user
        if not automatic:
            d = QtWidgets.QMessageBox(
                QtWidgets.QMessageBox.Information,
                'Update Checker', "You're all up to date!",
                QtWidgets.QMessageBox.Ok, self
            )

            return d.exec()

        else:
            self.LOGGER.info('This is the latest release.')
            self.statusBar().showMessage('No new releases available', 5 * 1000)

    # Debug methods
    def dump(self):
        """A utility method for calling all debug methods."""
        for name, inst in inspect.getmembers(self):
            if name.startswith('dump_') and inspect.isfunction(inst):
                # Get the method's signature
                s = inspect.signature(inst)

                # If the method has parameters, ignore it.
                if s.parameters:
                    self.LOGGER.debug(f'Ignoring debug method {self.__class__.__name__}.{name}.')
                    continue

                # Try to invoke the function.  If it fails,
                # log any exception that it generated.
                try:
                    inst()

                except Exception as e:
                    self.LOGGER.debug(f'Debug method {self.__class__.__name__}.{name} failed with exception '
                                      f'{e.__class__.__name__}!  ({e!s})')

    def dump_help_engine(self):
        """Dumps information from the QHelpEngineCore into the log file."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()

        # Dump check
        if not app.debug_mode or '--dump-help-engine' not in sys.argv:
            return

        # Dump information
        self.LOGGER.debug('Registered documentations:')

        for r in self.help_engine.registeredDocumentations():
            self.LOGGER.debug(f'{r} [{self.help_engine.documentationFileName(r)}]')

            self.LOGGER.debug(f'  - Documentation file(s)')
            for f in self.help_engine.files(r, []):  # type: QtCore.QUrl
                self.LOGGER.debug(f'    - {f.toDisplayString()}')

            self.LOGGER.debug('')
            self.LOGGER.debug(f'  - Filter attributes')
            for f in self.help_engine.filterAttributeSets(r):  # type: typing.List[typing.List[str]]
                self.LOGGER.debug(f'    - {len(f)} attribute(s)')

                for s in f:  # type: str
                    self.LOGGER.debug(f'      - {s}')

            self.LOGGER.debug('')
            self.LOGGER.debug('  - Custom filters')
            for f in self.help_engine.customFilters():  # type: str
                self.LOGGER.debug(f'    - {f}')

    def dump_extension_inheritance(self, ext: object):
        """Dumps the extension's inheritance tree into the log file."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        logger = logging.getLogger(f'{self.LOGGER.name}.loader')

        # Dump check
        if not app.debug_mode or '--dump-extension-inheritance' not in sys.argv:
            return

        # Dump inheritance
        for attr, inst in inspect.getmembers(ext):
            logger.debug(f'{ext.__class__.__name__} inheritance')

            for c in inspect.getmro(inst):
                # Get the module the class belongs to
                m = inspect.getmodule(c)
                package: typing.Optional[str] = None

                # Get the module's package (namespace)
                if m is not None:
                    package = m.__package__

                # Log it
                logger.debug(f'  - {package!s}.{c.__name__}')

    def dump_extension_namespace(self, before: typing.List[str], after: typing.List[str]):
        """Dumps the namespace before and after an extension load."""
        # Declarations
        app: QtWidgets.QApplication = QtWidgets.QApplication.instance()
        logger = logging.getLogger(f'{self.LOGGER.name}.loader')

        # Dump check
        if not app.debug_mode or '--dump-extension-namespace' not in sys.argv:
            return

        # Dump namespace before extension was loaded
        logger.debug(f'Before: {", ".join(before)}')

        # Dump namespace after extension was loaded
        logger.debug(f'After: {", ".join(after)}')

        # Dump newly loaded modules
        logger.debug('Extension modules: {}'.format(', '.join([m for m in after if m not in before])))

    # Events
    def moveEvent(self, event: QtGui.QMoveEvent):
        """An override for QMainWindow's default moveEvent.

        This override is responsible for processing move events and
        saving it to the settings file."""
        position: QtCore.QPoint = event.pos()

        self.settings['system']['window']['x'].value = position.x()
        self.settings['system']['window']['y'].value = position.y()

    def resizeEvent(self, event: QtGui.QResizeEvent):
        """An override for QMainWindow's default resizeEvent.

        This override is responsible for processing resize events
        and saving it to the settings file."""
        size: QtCore.QSize = event.size()

        self.settings['system']['window']['width'].value = size.width()
        self.settings['system']['window']['height'].value = size.height()

    def closeEvent(self, event: QtGui.QCloseEvent):
        """An override for the QMainWindow's default closeEvent.

        This override is responsible for processing closing operations,
        like saving user settings."""
        self.LOGGER.info('Performing closing operations...')

        self.LOGGER.info('Serializing settings...')
        try:
            d = json.dumps(self.settings.to_data())

        except ValueError as e:
            self.LOGGER.warning('Settings could not be serialized!')
            self.LOGGER.warning(f'Reason: {e.__cause__}')

        else:
            if not self._settings_file.isOpen():
                self._settings_file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text | QtCore.QFile.Truncate)

            if self._settings_file.isWritable():
                self.LOGGER.info('Saving settings...')
                self._settings_file.write(d.encode(encoding='UTF-8'))

            else:
                self.LOGGER.warning('Settings could not be saved!')
                self.LOGGER.warning(f'Reason: #{self._settings_file.error()} - {self._settings_file.errorString()}')

        finally:
            if self._settings_file.isOpen():
                self._settings_file.close()

        self.settings.close()
        self.LOGGER.info('Done!')
