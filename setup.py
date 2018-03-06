#!/usr/bin/env python3
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

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

setup(
    name="typesafety",
    description="Type safety checker for Python3",
    long_description= """\
Typesafety is a tool for writing type-checked code in Python. In languages
like C++, Java, etc., this is a language-level feature, but Python has no
such feature. With the advent of annotations it is however possible to write
code with type notations. Typesafety is a means to enforce that those notations
are valid.
""",
    license="LGPLv2+",
    version="2.1.2",
    author="Viktor Hercinger",
    author_email="viktor.hercinger@balabit.com",
    maintainer="Viktor Hercinger",
    maintainer_email="viktor.hercinger@balabit.com",
    keywords='nose type typesafe static',
    url="https://github.com/balabit/typesafety",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing',
        'Topic :: Documentation :: Sphinx',
    ],
    zip_safe=True,
    use_2to3=False,
    packages=['typesafety'],
    entry_points={
        'nose.plugins.0.10': [
            'typesafety = typesafety.noseplugin:TypesafetyPlugin'
        ],
        'pytest11': ['pytest_typesafety = typesafety.pytest_typesafety'],
    },
    install_requires=[
        'nose',
        'sphinx',
    ]
)
