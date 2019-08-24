from setuptools import find_packages
from setuptools import setup

setup(
    name="movienight",
    version="1.0.0",
    url="https://github.com/Unmoon/movienight",
    author="Unmoon",
    author_email="joona@unmoon.com",
    description="Simple VLC-based client that syncs video playback with remote server and other clients.",
    packages=find_packages(where=""),
    package_dir={"movienight": "movienight"},
    entry_points={"console_scripts": ["movienight=movienight.main:main"]},
    install_requires=["python-vlc", "pyqt5", "requests", "appdirs"],
    extras_require={"bundle": ["pyinstaller"]},
)
