# Movie Night
VLC-based media player that syncs with other players using Movie Night Server.

## Requirements

* Python 3.7
* [VLC](https://www.videolan.org/vlc/)

PyQt 5.13.0 does not bundle correctly with PyInstaller, so PyQt requirement has been frozen <5.13.0. 

Virtual environment should be created before installing or bundling the application.
```shell script
python -m venv venv
venv\Scripts\activate
python -m pip install -U pip setuptools
```

## Install in editable mode

`-e` allows editing the application without having to reinstall it.
```shell script
pip install -e .
movienight
```

## Build the bundle
### Windows

`Movie Night.exe` is generated in `dist`.
```shell script
pip install -e .[bundle]
pyinstaller main.spec
```

### Linux/Mac
TODO

## Codestyle

This project uses [Black](https://github.com/psf/black) for code formatting.

```shell script
pip install black
black movienight/
black setup.py
black main.spec
```
