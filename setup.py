#! /usr/bin/env python
# encoding: utf-8

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='PyVimeo',
    version='1.0.10',
    description='Simple interaction with the Vimeo API.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://developer.vimeo.com/',
    author='Vimeo',
    author_email='support@vimeo.com',
    packages=['vimeo', 'vimeo/auth'],
    install_requires=['requests>=2.4.0', 'tuspy==0.2.1'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet',
        'Topic :: Multimedia :: Video',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
