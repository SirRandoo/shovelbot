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

__all__ = [
    'recolor_html_links', 'invoke', 'get_callable_default_args',
    'get_callable_default_kwargs', 'get_callable_defaults', 'get_annotations'
]


class CallableDefaults(typing.NamedTuple):
    args: typing.Dict[str, typing.Any]
    kwargs: typing.Dict[str, typing.Any]


def get_annotations(func: typing.Callable) -> dict:
    """A special method for getting a callable's annotations.  This
    implementation is designed to support the future Python annotations."""


def recolor_html_links(html: str, hex_color: str) -> str:
    """Restyles all 'a' tags to display in the `hex_color` passed.
    
    **Note**: This is a destructive function.  Tags will be stripped of their
                existing styles."""


def get_callable_default_args(func: typing.Callable) -> dict:
    """Gets the default arguments of the callable `func`."""
    

def get_callable_default_kwargs(func: typing.Callable) -> dict:
    """Gets the default key-word arguments of the callable `func`."""


def get_callable_defaults(func: typing.Callable) -> CallableDefaults:
    """Gets the default arguments of the callable `func`."""


def invoke(func: typing.Callable, *args, unsafe: bool = None) -> typing.Any:
    """Calls the callable `func` with the arguments provided.
    The callable's arguments should be annotated, or provide a default.
    
    **Note**: This function maps the arguments passed to the arguments of the
                callable specified.  If the callable does not contain
                annotations, or a default value, that argument will omitted."""
