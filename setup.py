from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()


setup(
    name='pyupgrader',
    version='1.0.0b1',
    author='Noah Blaszak',
    author_email='70231827+Trogiken@users.noreply.github.com',
    description='Python library that allows the version of a program to be updated.',
    packages=['pyupgrader', 'pyupgrader.utilities'],
    package_data={'pyupgrader.utilities': ['default.yaml', 'comments.yaml']},
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'pyupgrader=pyupgrader.main_cli:cli'
        ]
    },
)
