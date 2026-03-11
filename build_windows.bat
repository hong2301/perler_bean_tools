@echo off
chcp 65001 >nul
title 拼豆识别系统 - Windows 打包工具
echo.
echo ╔══════════════════════════════════════════════════════════╗
echo ║                                                          ║
echo ║              🎨 拼豆识别系统 - Windows 打包              ║
echo ║                                                          ║
echo ╚══════════════════════════════════════════════════════════╝
echo.

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/5] Python 版本:
python --version
echo.

:: 检查并安装依赖
echo [2/5] 检查并安装打包依赖...
python -m pip install pyinstaller -q
if errorlevel 1 (
    echo [错误] 安装 PyInstaller 失败
    pause
    exit /b 1
)
echo     ✓ PyInstaller 已就绪
echo.

:: 清理旧的构建文件
echo [3/5] 清理旧的构建文件...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "__pycache__" rmdir /s /q "__pycache__"
echo     ✓ 清理完成
echo.

:: 开始打包
echo [4/5] 开始打包应用程序...
echo     注意：首次打包可能需要 5-10 分钟，请耐心等待...
echo.

pyinstaller bead_recognizer.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo [错误] 打包失败！请检查错误信息
    pause
    exit /b 1
)

echo.
echo [5/5] 打包完成！
echo.

:: 复制额外文件到输出目录
if exist "dist\拼豆识别系统" (
    echo 正在整理输出文件...
    xcopy /y "README.md" "dist\拼豆识别系统\" >nul 2>&1
    echo     ✓ 输出目录: dist\拼豆识别系统\
)

echo.
echo ═══════════════════════════════════════════════════════════
echo ✅ 打包成功！
echo.
echo 📁 输出位置: dist\拼豆识别系统\
echo 🚀 运行文件: dist\拼豆识别系统\拼豆识别系统.exe
echo.
echo 使用说明：
echo   1. 将整个 dist\拼豆识别系统 文件夹复制到目标电脑
echo   2. 双击运行 拼豆识别系统.exe
echo   3. 程序会自动打开浏览器访问服务
echo.
echo ═══════════════════════════════════════════════════════════
echo.
pause
