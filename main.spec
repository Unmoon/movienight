# -*- mode: python ; coding: utf-8 -*-

block_cipher = None
iconpath = os.path.join(os.path.dirname(os.path.abspath(SPEC)), "Movie Night.ico")


a = Analysis(
    ["movienight\\main.py"],
    pathex=["C:/Program Files/VideoLAN/VLC/"],
    binaries=[
        ("C:/Program Files/VideoLAN/VLC/plugins/*", "plugins"),
        ("C:/Program Files/VideoLAN/VLC/libvlc.dll", "."),
    ],
    datas=[("Movie Night.ico", ".")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Movie Night",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon=iconpath,
)
