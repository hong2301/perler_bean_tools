# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec 文件 - 拼豆识别系统打包配置
"""
import sys
import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
from PyInstaller.config import CONF

# 项目根目录
project_root = os.path.abspath(SPECPATH)

# 需要包含的数据文件
datas = [
    # (源路径, 目标目录)
    ('templates', 'templates'),
    ('uploads', 'uploads'),
    ('color.json', '.'),
    ('requirements.txt', '.'),
]

# 需要包含的隐藏导入
hiddenimports = [
    'flask',
    'werkzeug',
    'jinja2',
    'markupsafe',
    'itsdangerous',
    'click',
    'cv2',
    'numpy',
    'paddleocr',
    'openpyxl',
    'skimage',
    'pyyaml',
    'shapely',
    'scipy',
    'PIL',
    'lmdb',
    'tqdm',
    'requests',
    'visualdl',
    'paddle',
    'onnxruntime',
    'sklearn',
]

# 需要排除的模块（减小体积）
excludes = [
    'matplotlib',
    'tkinter',
    'PyQt5',
    'PyQt6',
    'PySide2',
    'PySide6',
    'wx',
    'pydoc',
    'doctest',
    'optparse',
    'sqlite3',
    'unittest',
    'xmlrpc',
    'pdb',
    'pydoc_data',
    'curses',
    'email',
    'html',
    'http',
    'xml',
]

# 分析主程序
a = Analysis(
    ['launcher.py'],  # 主程序入口（使用启动器）
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

# 创建 PYZ 存档
pyz = PYZ(a.pure, a.zipped_data)

# 配置 EXE
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='拼豆识别系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 显示控制台（方便查看启动日志）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='icon.ico',  # 如果有图标文件，取消注释
)

# 单文件模式（可选）
# 如果需要单文件版本，取消下面代码的注释
# coll = COLLECT(
#     exe,
#     a.binaries,
#     a.zipfiles,
#     a.datas,
#     strip=False,
#     upx=True,
#     upx_exclude=[],
#     name='拼豆识别系统'
# )
