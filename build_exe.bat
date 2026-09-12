@echo off
setlocal
cd /d "%~dp0"
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean PinkHelmetPet.spec
echo.
echo Build complete: dist\PinkHelmetPet\PinkHelmetPet.exe
pause
