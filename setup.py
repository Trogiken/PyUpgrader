from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='pyupdate',
    version='0.2.1',
    author='Noah Blaszak',
    author_email='70231827+Trogiken@users.noreply.github.com',
    description='Python library that allows the version of a program to be updated.',
    packages=['pyupdate', 'pyupdate.utilities', 'pyupdate.utilities.hashing'],
    package_data={'pyupdate.utilities': ['default.yml', 'comments.yml']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pyupdate=pyupdate.main_cli:cli'
        ]
    },
)
