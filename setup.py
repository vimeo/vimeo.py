#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='PyVimeo',
    version='0.3.9',
    description='Simple interaction with the Vimeo API.',
    url='https://developer.vimeo.com/',
    author='Vimeo',
    author_email='support@vimeo.com',
    license='Apache License, Version 2.0, January 2004',
    packages=['vimeo', 'vimeo/auth'],
    install_requires=['requests>=2.4.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Multimedia :: Video',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
