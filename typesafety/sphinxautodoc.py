#
# Copyright (c) 2013-2018 Balabit
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

import collections
import inspect


# This is a sphinx interface implementation so the number of
# arguments is outside our control.
def add_annotations_to_signature(
        app,
        what,
        name,
        obj,
        options,
        signature,
        return_annotation
):  # pylint: disable=R0913
    if what not in {"function", "method", "class"}:
        return None

    if what == "class":
        obj = obj.__init__
        what = "method"

        if not inspect.isfunction(obj):
            return None

    func = __extract_decorated_function(obj)
    arg_spec = inspect.getfullargspec(func)

    if not arg_spec.annotations:
        return None

    return __format_signature(what, func, arg_spec)


def __should_stop_resolution(obj, depth, *, maxdepth=100):
    return depth >= maxdepth or \
           not hasattr(obj, "decorated_function") or \
           not inspect.isfunction(obj.decorated_function)


def __extract_decorated_function(obj):
    depth = 0

    while not __should_stop_resolution(obj, depth):
        obj = obj.decorated_function
        depth += 1

    return obj


def __format_signature(type_str, function, arg_spec):
    return_type = __format_return_type(arg_spec)
    args = __format_args_and_kwargs(type_str, function, arg_spec)

    return (args, return_type)


def __format_return_type(arg_spec):
    annotations = arg_spec.annotations

    if "return" not in annotations:
        return ""

    return __format_type_annotation(annotations["return"])


def __format_type_annotation(annotation):
    if hasattr(annotation, "__name__"):
        result = annotation.__name__
        module = getattr(annotation, '__module__', 'builtins')
        if module != "builtins":
            result = module + '.' + result

        return result

    if isinstance(annotation, str):
        return repr(annotation)

    if isinstance(annotation, collections.Sequence):
        annotation_sequence = ", ".join(
            __format_type_annotation(t) for t in annotation
        )
        return "(" + annotation_sequence + ")"

    return str(annotation)


def __format_args_and_kwargs(type_str, function, arg_spec):
    args = __format_positional_args(type_str, function, arg_spec)
    annotations = arg_spec.annotations

    if arg_spec.varargs is not None:
        args.append("*%s" % __format_arg(arg_spec.varargs, annotations, {}))

    if arg_spec.kwonlyargs:
        args.append("*")
        args.extend(
            __format_args(
                arg_spec.kwonlyargs,
                annotations,
                arg_spec.kwonlydefaults
            )
        )

    if arg_spec.varkw is not None:
        args.append("**%s" % __format_arg(arg_spec.varkw, annotations, {}))

    return "(%s)" % ", ".join(args)


def __format_positional_args(type_str, function, arg_spec):
    arg_names, defaults = __remove_self_or_cls(type_str, function, arg_spec)
    defaults_by_name = __get_defaults_as_dict(arg_names, defaults)

    return __format_args(arg_names, arg_spec.annotations, defaults_by_name)


def __remove_self_or_cls(type_str, function, arg_spec):
    arg_names = arg_spec.args
    defaults = arg_spec.defaults

    if type_str == "method" or inspect.ismethod(function):
        if defaults is not None and len(defaults) == len(arg_names):
            defaults = defaults[1:]

        arg_names = arg_names[1:]

    return arg_names, defaults


def __get_defaults_as_dict(arg_names, defaults):
    defaults = defaults if defaults is not None else ()
    offset = len(arg_names) - len(defaults)

    return dict(zip(arg_names[offset:], defaults))


def __format_args(arg_names, annotations, defaults_by_name):
    args = []

    for arg_name in arg_names:
        args.append(__format_arg(arg_name, annotations, defaults_by_name))

    return args


def __format_arg(arg_name, annotations, defaults_by_name):
    name = __format_argument_name(arg_name, annotations)
    default_value_str = __format_default_value(arg_name, defaults_by_name)

    return "%s%s" % (name, default_value_str)


def __format_argument_name(arg_name, annotations):
    if arg_name not in annotations:
        return arg_name

    return arg_name + ": " + __format_type_annotation(annotations[arg_name])


def __format_default_value(arg_name, defaults_by_name):
    if not defaults_by_name or arg_name not in defaults_by_name:
        return ""

    return "=%s" % repr(defaults_by_name[arg_name])


def setup(app):
    app.connect("autodoc-process-signature", add_annotations_to_signature)
