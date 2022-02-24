#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
to install system wide use `pip install .`
testing is done via `python setup.py test`
'''

import subprocess
import setuptools


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as readme_file:
    readme = readme_file.read()

tag = ""

try:
    ps = subprocess.check_output(["git","describe","--tag"], stderr=subprocess.STDOUT)
    tag = ps.decode('utf-8').strip()
    tag = tag.replace("-", ".dev", 1).replace("-", "+")
except:
    tag = "0.dev0"

requirements = [
    "fonttools"
]

setup_requirements = [
	"pytest-runner", "pytest-pylint",
]
test_requirements = [
	"pytest", "pylint", "pyenchant",
]

setup(
    name='svg2mod',
    version=tag,
    description="Convert an SVG file to a KiCad footprint.",
    long_description_content_type='text/markdown',
    long_description=readme,
    author='https://github.com/svg2mod',
    author_email='',
    url='https://github.com/svg2mod/svg2mod',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts':['svg2mod = svg2mod.cli:main']},
    package_dir={'svg2mod':'svg2mod'},
    include_package_data=True,
    package_data={'kipart': ['*.gif', '*.png']},
    scripts=[],
    install_requires=requirements,
    license="GPLv2+",
    zip_safe=False,
    keywords='svg2mod, KiCAD, inkscape',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Intended Audience :: Manufacturing',
        'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
	setup_requires=setup_requirements,
    test_suite='test',
    tests_require=test_requirements
)
