from setuptools import setup

with open('README.md', encoding="utf-8") as f:
    readme = f.read()


setup(
    name='pyupgrader',
    version='2.1.9b1',
    author='Noah Blaszak',
    author_email='technology.misc@gmail.com',
    description='Keep your Python code up to date on client machines.',
    long_description=readme,
    long_description_content_type='text/markdown',
    project_urls={
        'Homepage': 'https://pypi.org/project/pyupgrader',
        'Documentation': 'https://github.com/Trogiken/PyUpgrader/wiki',
        'Release Notes': 'https://github.com/Trogiken/PyUpgrader/wiki/Release-Notes',
        'Source': 'https://github.com/Trogiken/PyUpgrader',
        'Issues': 'https://github.com/Trogiken/PyUpgrader/issues',
    },
    packages=['pyupgrader', 'pyupgrader.utilities'],
    install_requires=['pyyaml', 'requests', 'packaging', 'setuptools'],
    python_requires='>=3.8',
    entry_points={
        'console_scripts': [
            'pyupgrader=pyupgrader.main_cli:cli'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ]
)
