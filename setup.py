from setuptools import setup

with open('README.md') as f:
    readme = f.read()


setup(
    name='pyupgrader',
    version='1.0.5b1',
    author='Noah Blaszak',
    author_email='technology.misc@gmail.com',
    description='Keep your Python code up to date on client machines.',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/Trogiken/PyUpgrader',
    packages=['pyupgrader', 'pyupgrader.utilities'],
    package_data={'pyupgrader.utilities': ['default.yaml', 'comments.yaml']},
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
