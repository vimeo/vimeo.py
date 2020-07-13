#! /usr/bin/env python
# encoding: utf-8

from setuptools import setup

setup(name='PyVimeo',
    version='1.1.0',
    description='Simple interaction with the Vimeo API.',
    url='https://developer.vimeo.com/',
    author='Vimeo',
    author_email='support@vimeo.com',
    packages=['vimeo', 'vimeo/auth'],
    install_requires=['requests>=2.4.0', 'tuspy>=0.2.4'],
      python_requires='>=3.5',
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet',
        'Topic :: Multimedia :: Video',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
