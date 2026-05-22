# PyInstaller spec for xzqh GUI.
# Build:  pyinstaller packaging/xzqh-gui.spec --noconfirm
# Output: dist/xzqh-gui/xzqh-gui(.exe)  (onedir, see EXE.console below for onefile)

from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH).resolve().parent

a = Analysis(
    [str(project_root / "app" / "__main__.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=[],
    hiddenimports=[
        "tools.fetch_xzqh",
        "tools.generate_sql",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # The repo's dist/ and data/ are not bundled — users supply/refresh them at runtime.
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="xzqh-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="xzqh-gui",
)
