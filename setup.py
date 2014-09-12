#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import vimeo

setup(name='PyVimeo',
    version='.'.join(vimeo.version),
    description='Simple interaction with the Vimeo API.',
    author='Vimeo',
    author_email='support@vimeo.com',
    packages=['vimeo'],
    install_requires=['requests'],
)