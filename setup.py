#!/usr/bin/python

from distutils.core import setup

long_description = open('README.rst').read()

setup(name='fsutils', 
      version='0.4.0', 
      description='Utilities for working with FreeSurfer data', 
      author='Christian Haselgrove', 
      author_email='christian.haselgrove@umassmed.edu', 
      url='https://github.com/chaselgrove/fsutils', 
      packages=['fsutils'], 
      scripts=['fs_status', 'fs_slice', 'fs_slice_subjects'], 
      install_requires=['argparse', 
                        'python-dateutil', 
                        'numpy', 
                        'nibabel', 
                        'Pillow'], 
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
