"""
The MIT License (MIT)

Copyright (c) 2021 SirRandoo

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
import inspect
import typing
from collections import namedtuple

from bs4 import BeautifulSoup

__all__ = ['recolor_html_links', 'invoke', 'get_callable_default_args',
           'get_callable_default_kwargs', 'get_callable_defaults']

# noinspection PyTypeChecker
CallableDefaults = namedtuple('CallableDefaults', {'args', 'kwargs'})


def get_annotations(func):
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


def recolor_html_links(html, hex_color):
    html_soup = BeautifulSoup(html, "lxml")
    a_tags = html_soup.findAll("a")

    for tag in a_tags:
        if tag.get("href"):
            html = html.replace(str(tag), f"""<a href="{tag.get("href")}" style="color:{hex_color}">{tag.text}</a>""")

    return html


def get_callable_default_args(func):
    """Gets the default arguments the callable specified."""
    argspec = inspect.getfullargspec(func)

    if argspec.defaults:
        return {
            argspec.args[-x]: y
            for x, y in enumerate(reversed(argspec.defaults), 1)
            if isinstance(y, type(argspec.annotations.get(argspec.args[-x]))) or y is None
        }

    else:
        return {}


def get_callable_default_kwargs(func):
    argspec = inspect.getfullargspec(func)

    if argspec.kwonlydefaults:
        return argspec.kwonlydefaults

    else:
        return {}


def get_callable_defaults(func):
    """Gets the default arguments the callable specified."""
    return CallableDefaults(
        get_callable_default_args(func),
        get_callable_default_kwargs(func)
    )


def invoke(func, *args, unsafe=None):
    arg_spec = inspect.getfullargspec(func)
    arguments = {}

    if arg_spec.args and any([arg_spec.annotations.get(i) for i in arg_spec.args]):
        for arg in args:
            for anno, anno_class in arg_spec.annotations.items():
                if isinstance(arg, anno_class):
                    arguments[anno] = arg

        for bot_arg in ['shovelbot', 'bot', 'sb', 'client']:
            if bot_arg in arg_spec.args:
                for arg in args:
                    if arg.__class__.__name__ == 'ShovelBot':
                        arguments[bot_arg] = arg

    if arg_spec.kwonlyargs and any([arg_spec.annotations.get(i) for i in arg_spec.kwonlyargs]):
        for arg in args:
            for anno, anno_class in [(k, v) for k, v in arg_spec.annotations.items() if k in arg_spec.kwonlyargs]:
                if isinstance(arg, anno_class):
                    arguments[anno] = arg

        for bot_arg in ['shovelbot', 'bot', 'sb', 'client']:
            if bot_arg in arg_spec.kwonlyargs:
                for arg in args:
                    if arg.__class__.__name__ == 'ShovelBot':
                        arguments[bot_arg] = arg

    if not unsafe:
        try:
            func(**arguments)

        except Exception as e:
            raise ValueError from e

    else:
        return func(**arguments)
