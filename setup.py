from setuptools import setup, find_packages

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stackexchangepy',
    version='0.0.2',
    description='Stackexchange API Wrapper',
    long_description=long_description,
    url='https://github.com/monzita/stackexchangepy',
    author='Monika Ilieva',
    author_email='hidden@hidden.com',
    install_requires = ['requests', 'tinynetrc'],
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Topic :: Software Development :: Build Tools',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Programming Language :: Python :: 3.6'
    ],

    keywords='stackexchange api wrapper python3',
    packages=find_packages(exclude=['contrib', 'docs', 'tests', 'venv']),
)