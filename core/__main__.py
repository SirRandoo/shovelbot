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
import json
import logging
import pathlib
import subprocess

import PySide6
import sys
import traceback
import typing

import click
from PySide6 import QtCore, QtNetwork, QtWidgets

from QtUtilities import settings
from QtUtilities.utils import qmessage_handler
from utils.custom import QApp

# Declarations
application = QApp(sys.argv)


# Custom exception handler
# noinspection PyArgumentList
def syshook(except_class: typing.Type[Exception], except_instance: Exception, trace):
    """A custom syshook for handling exceptions."""
    error_segments = [f'{except_class.__name__}: {except_instance!s}']

    for m in traceback.format_tb(trace):
        m = m.replace(f'{QtCore.QDir.currentPath()}/', '')
        error_segments += m.splitlines()

    # "Cleanly" report the error
    application.logger.exception(error_segments[0], exc_info=(except_class, except_instance, trace))

    dialog = QtWidgets.QMessageBox(
        QtWidgets.QMessageBox.Critical, 'Error Handler',
        f'Cause: {except_class.__name__}({except_instance!s})\t',
        QtWidgets.QMessageBox.Ok
    )

    dialog.setInformativeText(
        f'You can submit a bug report <a href="{application.client.REPOSITORY.toDisplayString()}/issues/new">here</a>.'
    )

    dialog.setDetailedText(f'{error_segments[0]}\n' + '\n'.join(error_segments[1:]))

    dialog.show()
    dialog.exec()
    application.quit()


# Assign the above handler to the interpreter's excepthook
sys.excepthook = syshook


@click.group(invoke_without_command=True)
@click.pass_context
def entry(ctx: click.Context):
    if ctx.invoked_subcommand is None:
        ctx.invoke(entry_run)


@entry.command(
    name='update',
    help="Runs the application's built-in dependency updater."
)
@click.option(
    '--settings-file',
    type=pathlib.Path,
    default=f'{application.applicationName()}.settings',
    envvar='SBSETTINGS',
    allow_from_autoenv=True,
    help="A file path where the application's settings will be stored."
)
@click.option(
    '--extensions',
    type=pathlib.Path,
    envvar='SBEXT',
    allow_from_autoenv=True,
    help='A directory to look for extensions.  If this is passed, the '
         'application will not load use the directory in the settings file, '
         'if it exists.'
)
def entry_update(settings_file: pathlib.Path, extensions: pathlib.Path = None):
    # TODO: Maybe also update the application?
    click.echo(f'Updating {application.applicationDisplayName()}...')

    # Declarations
    app_requirements = pathlib.Path('requirements.txt')

    # Validate the application's requirements.txt file
    if not app_requirements.exists():
        sys.exit("The application's requirements.txt file is missing!")

    # Update the application's dependencies
    with app_requirements.open() as INFILE:
        with click.progressbar(
                iterable=INFILE.readlines(),
                label='Updating dependencies...',
                show_percent=True,
                show_eta=True,
                show_pos=True,
                bar_template='▐%(bar)s▌ %(label)s %(info)s',
                fill_char='█',
                empty_char='▒'
        ) as progress:
            for dep in progress:  # type: str
                if dep.startswith('git'):
                    _, egg = dep.split('#')
                    _, d = egg.split('=')

                    progress._label = f'Updating {d}...'

                else:
                    progress._label = f'Updating {dep}...'

                # Run pip
                subprocess.run([sys.executable, '-m', 'pip', 'install', '-U', dep],
                               stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL)

    # Validate the extensions argument
    if extensions is None:
        click.echo("You didn't specify an extensions directory; we'll just look in the settings file...")

        if settings_file.exists():
            with settings_file.open() as INFILE:
                try:
                    settings_raw = json.load(INFILE)

                except ValueError:
                    click.echo("You settings file couldn't be loaded!")
                    click.echo("If you've freshly generate it, you should report a bug @ "
                               f"{application.client.REPOSITORY.toDisplayString()}/issues/new")
                    click.echo(f'If your settings file is from a prior version of '
                               f'{application.applicationDisplayName()}, you should check to see if older settings '
                               f'files will need to be discarded/imported at '
                               f'{application.client.REPOSITORY.toDisplayString()}/releases/'
                               f'v{application.applicationVersion()}')

                    if click.confirm('Do you want to manually input your extensions directory?', abort=True):
                        extensions = click.prompt('Extension directory', type=pathlib.Path)

                else:
                    click.echo('Translating settings file...')
                    t = []

                    for segment in settings_raw:
                        t.append(settings.Setting.from_data(segment))

                    # Attempt to locate the extensions directory
                    for s in t:
                        if s.key == 'extensions':
                            try:
                                d = pathlib.Path(s['directory'].value)

                            except KeyError:
                                click.echo('Your settings file is missing a couple of settings!')
                                click.echo("If you've freshly generate it, you should report a bug @ "
                                           f"{application.client.REPOSITORY.toDisplayString()}/issues/new")
                                click.echo(f'If your settings file is from a prior version of '
                                           f'{application.applicationDisplayName()}, you should check to see if older '
                                           f'settings files will need to be discarded/imported at '
                                           f'{application.client.REPOSITORY.toDisplayString()}/releases/'
                                           f'v{application.applicationVersion()}')

                                if click.confirm('Do you want to manually input your extensions directory?',
                                                 abort=True):
                                    extensions = click.prompt('Extension directory', type=pathlib.Path)

                            else:
                                extensions = d

        else:
            click.echo("Your settings file doesn't exist!")

            if click.confirm('Do you want to manually input your extensions directory?', abort=True):
                extensions = click.prompt('Extension directory', type=pathlib.Path)

    # Extensions validation
    if extensions is None:
        sys.exit("An extensions directory wasn't found in your settings file, nor manually given!")

    else:
        if not extensions.exists():
            extensions.mkdir(parents=True, exist_ok=True)

    # Iterate over the extensions in the directory
    for ext in extensions.iterdir():
        if not ext.is_dir() or ext.name.startswith('_'):
            continue  # Ignore files and internal directories, like __pycache__

        # Ensure the extension has a requirements.txt file
        ext_requirements = ext.joinpath('requirements.txt')

        if not ext_requirements.exists():
            continue

        click.echo(f'Updating dependencies for extension "{ext!s}"')
        with ext_requirements.open() as INFILE:
            with click.progressbar(
                    iterable=INFILE.readlines(),
                    label='Updating dependencies...',
                    show_percent=True,
                    show_eta=True,
                    show_pos=True,
                    bar_template='▐%(bar)s▌ %(label)s %(info)s',
                    fill_char='█',
                    empty_char='▒'
            ) as progress:
                for dep in progress:  # type: str
                    if dep.startswith('git'):
                        _, egg = dep.split('#')
                        _, d = egg.split('=')

                        progress._label = f'Updating {d}...'

                    else:
                        progress._label = f'Updating {dep}...'

                    # Run pip
                    subprocess.run([sys.executable, '-m', 'pip', 'install', '-U', dep],
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)


# noinspection PyUnusedLocal
@entry.command(
    name='run',
    short_help=f'Runs {application.applicationDisplayName()}',
    context_settings={'ignore_unknown_options': True}
)
@click.option(
    '--debug',
    is_flag=True,
    envvar='Sb.Debug',
    allow_from_autoenv=True,
    help='Whether or not the application is in debug mode.  While in debug '
         'mode, more log statements are outputted into the log file.'
)
@click.option(
    '--disable-updater',
    is_flag=True,
    envvar='Sb.NoUpdater',
    allow_from_autoenv=True,
    help="Whether or not the application's update checker is enabled or not.  "
         "This overrides the value in the settings file."
)
@click.option(
    '--redirect-policy',
    type=int,
    envvar='Sb.RedirectPolicy',
    allow_from_autoenv=True,
    default=QtNetwork.QNetworkRequest.NoLessSafeRedirectPolicy,
    help="How the application will handle redirects.  For more information "
         "about redirect policies, visit Qt5's documentation page on them: "
         "https://doc.qt.io/qt-5/qnetworkrequest.html#RedirectPolicy-enum"
)
@click.argument('extra', nargs=-1, type=click.UNPROCESSED)
def entry_run(debug: bool, disable_updater: bool, redirect_policy: int, extra):
    # Populate the application's attributes
    application.debug_mode = debug
    application.disable_updater = disable_updater

    # Set the QNetworkAccessManager's redirect policy to the one specified
    application.set_redirect_policy(redirect_policy)

    # Set up the logging module
    level = logging.INFO
    handlers = [logging.FileHandler(f'{application.applicationName()}.log', mode='w')]

    if debug:
        level = logging.DEBUG
        handlers.append(logging.StreamHandler())

    logging.basicConfig(
        format='[{asctime}][{levelname}][{filename}:{funcName}:{lineno}][{name}] {message}',
        style='{', datefmt='%H:%M:%S',
        level=level, handlers=handlers
    )

    # Set up the Qt5 logger
    QtCore.qInstallMessageHandler(qmessage_handler)

    # Run the application
    return application.exec()


@entry.command(
    name='info',
    short_help=f'Shows information about {application.applicationDisplayName()}'
)
def entry_info():
    click.echo_via_pager(
        f'{application.client.__doc__}\n'
        f'\n'
        f'Created by {", ".join(application.client.AUTHORS)}\n'
        f'\n'
        f"This software is licensed under {application.client.LICENSE}.  You're free to modify and "
        f"redistribute it under the conditions of the aforementioned license.  If you want to read "
        f"more about it, you can read the LICENSE file you should've received along side your "
        f"download.  Alternatively, you can read more about it on its website at "
        f"{application.client.LICENSE_URL.toDisplayString()}\n"
        f"\n"
        f"The application's source code can be found at {application.client.REPOSITORY.toDisplayString()}\n"
        f'\n'
        f"You're currently running version {application.applicationVersion()}.  You can view the "
        f"changelog for this release at "
        f"{application.client.REPOSITORY.toDisplayString()}/releases/tag/v{application.applicationVersion()}\n"
        f'\n'
        f'Version: {application.applicationVersion()}\n'
        f'Qt Version: {PySide6.__version__}'
    )


entry()
