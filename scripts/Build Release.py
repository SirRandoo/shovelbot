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
import os
import pathlib
import shutil
import typing
import zipfile


class ReleaseBuilder:
    """Constructs a new release."""
    LOGGER = logging.getLogger("core.release_builder")
    
    def __init__(self, *args, **kwargs):
        self.build: str = kwargs.get('build')
        self.python_directory: str = '_python'
        
        self.locations: typing.Dict[str, pathlib.Path] = {
            'python32': pathlib.Path(os.getenv('WORKSPACE')).joinpath('Python Resources/python-3.7.4-embed-win32.zip'),
            'python64': pathlib.Path(os.getenv('WORKSPACE')).joinpath('Python Resources/python-3.7.4-embed-amd64.zip'),
            'get-pip': pathlib.Path(os.getenv('WORKSPACE')).joinpath('Python Resources/get-pip.py'),
            'modify-pth': pathlib.Path(os.getenv('WORKSPACE')).joinpath('Python Resources/modify-pth.py')
        }
    
    @staticmethod
    def get_python_wrapper(directory: pathlib.Path) -> str:
        return f'{directory.joinpath("python.exe")!s} %*'
    
    @staticmethod
    def get_bot_wrapper(directory: pathlib.Path) -> str:
        return f'{directory.joinpath("python.exe")!s} core %*'
    
    def generate_wrappers(self):
        python_executable = str(pathlib.Path(f'./{self.python_directory}').joinpath('python.exe'))
        
        with open(f'build/shovelbot.bat', 'w') as OUTFILE:
            OUTFILE.writelines([
                '@echo off\n',
                self.get_bot_wrapper(pathlib.Path(f'./{self.python_directory}')) + '\n'
            ])
        
        with open(f'build/setup.bat', 'w') as OUTFILE:
            OUTFILE.writelines([
                '@echo off\n',
                '\n',
                'echo Preparing local python distributable for setup...\n',
                f'"{python_executable}" {self.python_directory}/modify-pth.py\n',
                'echo Installing pip...\n'
                f'"{python_executable}" {self.python_directory}/get-pip.py\n',
                "echo Installing ShovelBot's required libraries...\n",
                f'"{python_executable}" -m pip install -U -r \"requirements.txt\"\n',
                "echo Running ShovelBot's updater...\n",
                f'shovelbot update --extensions=\"extensions\"\n',
                "echo Setup complete!\n",
                f'shovelbot info\n',
                'echo Deleting setup.bat...\n',
                'pause\n',
                f'"{python_executable}" -c "import os; os.unlink(\'setup.bat\')"\n'
            ])
    
    def build_release(self):
        if os.path.exists('build'):
            shutil.rmtree('build')
        os.mkdir('build')
        
        if not os.path.exists(f'build/{self.python_directory}'):
            os.mkdir(f'build/{self.python_directory}/')
        
        with zipfile.ZipFile(self.locations[f'python{self.build}']) as INFILE:
            for file in INFILE.filelist:  # type: zipfile.ZipInfo
                with open(f'build/{self.python_directory}/{file.filename}', 'wb') as OUTFILE:
                    OUTFILE.write(INFILE.read(file.filename))
        
        self.generate_wrappers()
        shutil.copyfile(str(self.locations['get-pip']), f'build/{self.python_directory}/get-pip.py')
        
        with open(f'build/{self.python_directory}/modify-pth.py', 'w') as OUTFILE:
            OUTFILE.writelines([
                'import sys\n',
                'import re\n',
                'import os',
                '\n',
                '\n',
                'if __name__ == "__main__":\n',
                '\tprint("Modifying interpreter\'s path...")\n',
                '\t\n',
                '\tpy_ver = f"{sys.version_info.major}{sys.version_info.minor}"\n'
                '\tpy_zip = f"python{py_ver}.zip"\n',
                '\tpy_path = os.path.join(sys.prefix, f"python{py_ver}._pth")\n',
                '\t\n',
                '\twith open(py_path, "w") as OUTFILE:\n',
                '\t\tOUTFILE.write(f"..\\n")\n'
                '\t\tOUTFILE.write(f"../core\\n")\n'
                '\t\tOUTFILE.write(f"{py_zip}\\n")\n',
                '\t\tOUTFILE.write(f".\\n")\n',
                '\t\tOUTFILE.write("Lib\\n")\n',
                '\t\tOUTFILE.write("Lib/site-packages\\n")\n',
                '\tprint("Modified!")'
            ])
        
        shutil.copytree('core', 'build/core')
        shutil.copytree('extensions', 'build/extensions')
        shutil.copytree('resources', 'build/resources')
        shutil.copytree('data', 'build/data')
        shutil.copyfile('README.md', 'build/README.md')
        shutil.copyfile('requirements.txt', 'build/requirements.txt')
        shutil.copyfile('LICENSE', 'build/LICENSE')
        shutil.copyfile('CHANGES.md', 'build/CHANGES.md')
        
        if not os.path.exists('out'):
            os.mkdir('out')
        
        with zipfile.ZipFile(f'out/ShovelBot_x{self.build}.zip', 'w') as INFILE:
            for dirname, dirs, files in os.walk('build'):
                if dirname == '__pycache__':
                    continue
                
                directory = pathlib.Path(os.path.normpath(dirname).replace('build\\', '', 1))
                
                for file in files:  # type: str
                    path = os.path.join(directory, file)
                    
                    if dirname in ['.', 'build']:
                        path = file
                    
                    with INFILE.open(path, 'w') as OUTFILE:
                        with open(os.path.join(dirname, file), 'rb') as INFILE2:
                            OUTFILE.write(INFILE2.read())
        
        shutil.rmtree('build')


if __name__ == '__main__':
    print('Building 64bit release....')
    ReleaseBuilder(build='64').build_release()
    
    print('Building 32bit release....')
    ReleaseBuilder(build='32').build_release()
