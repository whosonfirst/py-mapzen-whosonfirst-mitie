#!/usr/bin/env python

# Remove .egg-info directory if it exists, to avoid dependency problems with
# partially-installed packages (20160119/dphiffer)

import os, sys
from shutil import rmtree

cwd = os.path.dirname(os.path.realpath(sys.argv[0]))
egg_info = cwd + "/mapzen.whosonfirst.mitie.egg-info"
if os.path.exists(egg_info):
    rmtree(egg_info)

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read()
version = open("VERSION").read()

setup(
    name='mapzen.whosonfirst.mitie',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.mitie'],
    version=version,
    description='Tools and libraries for working with Who\'s On First data and the MITIE tool-chain',
    author='Mapzen',
    url='https://github.com/whosonfirst/py-mapzen-whosonfirst-mitie',
    install_requires=[
        'mapzen.whosonfirst.placetypes>=0.11',
        'mapzen.whosonfirst.search>=0.12',
        ],
    dependency_links=[
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-placetypes/tarball/master#egg=mapzen.whosonfirst.placetypes-0.11'
        'https://github.com/whosonfirst/py-mapzen-whosonfirst-search/tarball/master#egg=mapzen.whosonfirst.search-0.12'
        ],
    packages=packages,
    scripts=[
        ],
    download_url='https://github.com/whosonfirst/py-mapzen-whosonfirst-mitie/releases/tag/v0.01',
    license='BSD')
