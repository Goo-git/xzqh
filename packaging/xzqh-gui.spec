# PyInstaller spec for xzqh GUI - portable single-file build.
# Build:  pyinstaller packaging/xzqh-gui.spec --noconfirm
# Output: dist/xzqh-gui.exe (Windows) or dist/xzqh-gui (macOS) / dist/xzqh-gui.app

import sys
from pathlib import Path

block_cipher = None
project_root = Path(SPECPATH).resolve().parent
assets_dir = project_root / "assets"

# Platform-aware icon selection. PyInstaller picks the first match.
icon_candidates = []
icns = assets_dir / "icon.icns"
ico = assets_dir / "icon.ico"
png = assets_dir / "icon.png"
if sys.platform == "darwin" and icns.exists():
    icon_candidates.append(str(icns))
if ico.exists():
    icon_candidates.append(str(ico))
if png.exists():
    icon_candidates.append(str(png))
exe_icon = icon_candidates[0] if icon_candidates else None

# Bundle the PNG so MainWindow can set the window icon at runtime.
datas = []
if png.exists():
    datas.append((str(png), "assets"))

a = Analysis(
    [str(project_root / "app" / "__main__.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "tools.fetch_xzqh",
        "tools.generate_sql",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "tkinter",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# ---- onefile: pack binaries, zipfiles, datas directly into the EXE ----
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="xzqh-gui",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=exe_icon,
)

# On macOS, wrap into a .app bundle so it shows the icon and double-clicks
# from Finder. PyInstaller emits both ``xzqh-gui`` and ``xzqh-gui.app`` in dist/.
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name="xzqh-gui.app",
        icon=exe_icon,
        bundle_identifier="com.goo-git.xzqh.gui",
        info_plist={
            "CFBundleName": "xzqh GUI",
            "CFBundleDisplayName": "xzqh GUI",
            "CFBundleShortVersionString": "2025.12.31",
            "NSHighResolutionCapable": True,
        },
    )
