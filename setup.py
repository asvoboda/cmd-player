from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='cmdplayer',
    version='0.0.1',
    description='A simple command line based music player',
    url='https://github.com/asvoboda/cmd-player',
    author='Andrew Svoboda',
    author_email='svoboda.andrew@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='audio',
    install_requires=['mutagen', 'pyreadline'],
    scripts=['player.py'],
    entry_points={
        'console_scripts': [
            'player=player:main',
        ],
    },
)