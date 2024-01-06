from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='pyupdate',
    version='0.1.0',
    author='Noah Blaszak',
    author_email='70231827+Trogiken@users.noreply.github.com',
    description='Python library that allows the version of a program to be updated.',
    packages=['pyupdate'],
    install_requires=requirements,
)
