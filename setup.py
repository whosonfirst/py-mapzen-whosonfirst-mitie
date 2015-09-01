#!/usr/bin/env python

from setuptools import setup, find_packages

packages = find_packages()
desc = open("README.md").read(),

setup(
    name='mapzen.whosonfirst.mitie',
    namespace_packages=['mapzen', 'mapzen.whosonfirst', 'mapzen.whosonfirst.mitie'],
    version='0.01',
    description='Tools and libraries for working with Who\'s On First data and the MITIE tool-chain',
    author='Mapzen',
    url='https://github.com/mapzen/py-mapzen-whosonfirst-mitie',
    install_requires=[
        'mapzen.whosonfirst.placetypes',
        ],
    dependency_links=[
        ],
    packages=packages,
    scripts=[
        ],
    download_url='https://github.com/whosonfirst/py-mapzen-whosonfirst-mitie/releases/tag/v0.01',
    license='BSD')
