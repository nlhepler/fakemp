#!/usr/bin/env python

from __future__ import division, print_function

import sys

from os.path import abspath, join, split
from setuptools import setup

sys.path.insert(0, join(split(abspath(__file__))[0], 'lib'))
from fakemp import __version__ as _fakemp_version

setup(name='fakemp',
      version=_fakemp_version,
      description='Fake multiprocessing pool objects',
      author='N Lance Hepler',
      author_email='nlhepler@gmail.com',
      license='GNU GPL version 3',
      packages=['fakemp'],
      package_dir={'fakemp': 'lib/fakemp'},
      requires=['six']
     )
