#!/usr/bin/env python

from setuptools import setup

setup(name='fakemp',
      version='0.9.0',
      description='Fake multiprocessing pool objects',
      author='N Lance Hepler',
      author_email='nlhepler@gmail.com',
      license='GNU GPL version 3',
      packages=['fakemp'],
      package_dir={'fakemp': 'src/fakemp'},
     )
