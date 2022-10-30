#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Grant Paton-Simpson",
    author_email='grant@sofastatistics.com',
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.10',
    ],
    description="SOFA Statistics freshened up",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='sofalite',
    name='sofalite',
    packages=find_packages(include=['sofalite', 'sofalite.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/grantps/sofalite',
    version='0.1.0',
    zip_safe=False,
)
