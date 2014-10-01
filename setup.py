#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import vimeo

setup(name='PyVimeo',
    version='.'.join(str(v) for v in vimeo.version),
    description='Simple interaction with the Vimeo API.',
    author='Vimeo',
    author_email='support@vimeo.com',
    packages=['vimeo'],
    install_requires=['requests>=2.4.0'],
)