#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='PyVimeo',
    version='0.1.1',
    description='Simple interaction with the Vimeo API.',
    author='Vimeo',
    author_email='support@vimeo.com',
    packages=['vimeo', 'vimeo/auth'],
    install_requires=['requests>=2.4.0'],
)
