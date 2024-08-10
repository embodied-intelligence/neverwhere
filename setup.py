from os import path

from setuptools import setup, find_packages

with open(path.join(path.abspath(path.dirname(__file__)), 'VERSION'), encoding='utf-8') as f:
    version = f.read()

with open(path.join(path.abspath(path.dirname(__file__)), 'README'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='neverwhere',
      packages=find_packages(),
      install_requires=[
          "params-proto",
          "numpy",
          "pillow",
      ],
      description=long_description.split('\n')[0],
      long_description=long_description,
      author='Ge Yang<ge.ike.yang@gmail.com>',
      url='https://github.com/embodied-intelligence/neverwhere',
      author_email='ge.ike.yang@gmail.com',
      package_data={'neverwhere': ['neverwhere', 'neverwhere/*.*']},
      version=version)
