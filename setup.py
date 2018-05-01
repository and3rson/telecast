#!/usr/bin/env python3.6

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='telecast',
    # use_scm_version=True,
    # setup_requires=['setuptools_scm'],
    description='Portable REST/JSON RPC implementation.',
    long_description=long_description,
    url='https://github.com/and3rson/telecast',
    author='Andrew Dunai',
    author_email='a@dun.ai',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='python json rest rpc',
    packages=[
        'telecast',
        'telecast.contrib',
        'telecast.contrib.django',
        'telecast.contrib.rest_framework'
    ],
)
