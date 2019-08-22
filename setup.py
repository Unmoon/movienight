from setuptools import find_packages
from setuptools import setup

setup(
    name="movienight",
    version="1.0.0",
    url="",
    author="Unmoon",
    author_email="joona@unmoon.com",
    description="Simple VLC-based client that syncs video playback with remote server and other clients.",
    packages=find_packages(where="src"),
    package_dir={"movienight": "src/movienight"},
    entry_points={"console_scripts": ["movienight=movienight.main:main"]},
    install_requires=["python-vlc", "pyqt5", "requests"],
    extras_require={"package": ["pyinstaller"]},
)
