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
import inspect
import typing

from bs4 import BeautifulSoup

__all__ = ['recolor_html_links', 'safe_call', 'invoke',
           'get_callable_default_args', 'get_callable_default_kwargs',
           'get_callable_defaults']


def get_annotations(func: typing.Callable) -> dict:
    """A special method for getting a callable's annotations.  This
    implementation is designed to support the future Python annotations."""
    annotations = inspect.getfullargspec(func).annotations
    signature = inspect.signature(func)
    converted = typing.get_type_hints(func)
    a = {}
    
    if all([type(v) == str for v in signature.parameters.values()]):
        a = {k: annotations[k] for k in signature.parameters}
    
    else:
        a = {k: v for k, v in signature.parameters.items()}
    
    return a


def recolor_html_links(html: str, hex_color: str) -> str:
    """Restyles all 'a' tags to display in the hex color
    passed (`hex_color`).
    
    This is a destructive function.  Tags will be stripped
    of their existing styles!"""
    html_soup = BeautifulSoup(html, "lxml")
    a_tags = html_soup.findAll("a")
    
    for tag in a_tags:
        if tag.get("href"):
            html = html.replace(str(tag), f"""<a href="{tag.get("href")}" style="color:{hex_color}">{tag.text}</a>""")
    
    return html


def safe_call(func: typing.Callable, *args, **kwargs):
    """A utility callable for calling callables.
    This is primarily used to call 3rd party callables.
    Should the callable raise an exception, the exception
    will be caught and logged, then a ValueError will be
    raised.  The sole reason for raising ValueError is
    to ensure we can always handle any exception thrown
    at the bot."""
    try:
        return func(*args, **kwargs)
    
    except Exception as e:
        raise ValueError from e


def get_callable_default_args(func: typing.Callable) -> dict:
    """Gets the default arguments the callable specified."""
    argspec = inspect.getfullargspec(func)
    
    if argspec.defaults:
        return {argspec.args[-x]: y for x, y in enumerate(reversed(argspec.defaults), 1) if
                isinstance(y, type(argspec.annotations.get(argspec.args[-x]))) or y is None}
    
    else:
        return dict()


def get_callable_default_kwargs(func: typing.Callable) -> dict:
    """Gets the default key-word arguments the callable specified."""
    argspec = inspect.getfullargspec(func)
    
    if argspec.kwonlydefaults:
        return argspec.kwonlydefaults
    
    else:
        return dict()


def get_callable_defaults(func: typing.Callable) -> dict:
    """Gets the default arguments the callable specified."""
    return dict(
        args=get_callable_default_args(func),
        kwargs=get_callable_default_kwargs(func)
    )


def invoke(func: typing.Callable, *args, unsafe: bool = None) -> typing.Any:
    """Calls the callable `func` with the arguments provided.
    The callable's arguments should be annotated, or provide
    a default."""
    arg_spec = inspect.getfullargspec(func)  # Get the argspec of the callable
    arguments = dict()  # The arguments we'll be passed to the callable
    
    if arg_spec.args and any([arg_spec.annotations.get(i) for i in arg_spec.args]):
        for arg in args:
            for anno, anno_class in arg_spec.annotations.items():
                if isinstance(arg, anno_class):
                    arguments[anno] = arg
        
        for bot_arg in ["shovelbot", "bot", "sb", "client"]:
            if bot_arg in arg_spec.args:
                for arg in args:
                    if arg.__class__.__name__ == "ShovelBot":
                        arguments[bot_arg] = arg
    
    if arg_spec.kwonlyargs and any([arg_spec.annotations.get(i) for i in arg_spec.kwonlyargs]):
        for arg in args:
            for anno, anno_class in [(k, v) for k, v in arg_spec.annotations.items() if k in arg_spec.kwonlyargs]:
                if isinstance(arg, anno_class):
                    arguments[anno] = arg
        
        for bot_arg in ["shovelbot", "bot", "sb", "client"]:
            if bot_arg in arg_spec.kwonlyargs:
                for arg in args:
                    if arg.__class__.__name__ == "ShovelBot":
                        arguments[bot_arg] = arg
    
    if not unsafe:
        return safe_call(func, **arguments)
    
    else:
        return func(**arguments)
