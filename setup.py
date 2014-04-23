#!/usr/bin/python

from distutils.core import setup

long_description = open('README.rst').read()

setup(name='fsutils', 
      version='0.1.0', 
      description='Utilities for working with FreeSurfer data', 
      author='Christian Haselgrove', 
      author_email='christian.haselgrove@umassmed.edu', 
      url='https://github.com/chaselgrove/fsutils', 
      scripts=['fs_status'], 
      install_requires=['argparse', 'python-dateutil'], 
      classifiers=['Development Status :: 3 - Alpha', 
                   'Environment :: Console', 
                   'Intended Audience :: Science/Research', 
                   'License :: OSI Approved :: BSD License', 
                   'Operating System :: OS Independent', 
                   'Programming Language :: Python', 
                   'Topic :: Scientific/Engineering'], 
      license='BSD license', 
      long_description=long_description
     )

# eof
