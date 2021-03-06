from setuptools import find_packages
from setuptools import setup

setup(
    name="movienight",
    version="1.0.0",
    url="https://github.com/Unmoon/movienight",
    author="Unmoon",
    author_email="joona@unmoon.com",
    description="VLC-based media player that syncs with other players using Movie Night Server.",
    packages=find_packages(where=""),
    package_dir={"movienight": "movienight"},
    entry_points={"console_scripts": ["movienight=movienight.__main__:main"]},
    install_requires=["python-vlc", "pyqt5<5.13.0", "requests", "appdirs"],
    extras_require={"bundle": ["pyinstaller"]},
)
