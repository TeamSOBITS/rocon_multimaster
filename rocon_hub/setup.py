#!/usr/bin/env python3

from distutils.core import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rocon_hub'],
    package_dir={'': 'src'},
    requires=['redis']
)

setup(**d)
