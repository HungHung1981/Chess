@echo off
setlocal
cd /d "%~dp0"

echo Building the Stockfish terminal chess game...
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.10 or newer was not found on PATH.
    exit /b 1
)
set "PYTHON_EXE="
for /f "delims=" %%P in ('where python') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (
    echo ERROR: Could not locate Python on PATH.
    exit /b 1
)
"%PYTHON_EXE%" -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10 or newer is required.
    exit /b 1
)

if not defined MSYS2_ROOT if exist "%~d0\msys64\mingw64\bin\g++.exe" set "MSYS2_ROOT=%~d0\msys64"
if defined MSYS2_ROOT set "PATH=%MSYS2_ROOT%\mingw64\bin;%MSYS2_ROOT%\usr\bin;%PATH%"

where make >nul 2>nul
if errorlevel 1 (
    echo ERROR: GNU make was not found on PATH.
    echo Install MSYS2, then add its usr\bin directory to PATH.
    exit /b 1
)

where g++ >nul 2>nul
if errorlevel 1 (
    echo ERROR: GCC was not found on PATH.
    echo Install MSYS2 MINGW64 GCC and add its mingw64\bin directory to PATH.
    exit /b 1
)

for /f "tokens=1 delims=." %%V in ('g++ -dumpversion 2^>nul') do set GCC_MAJOR=%%V
if not defined GCC_MAJOR (
    echo ERROR: Could not determine the GCC version.
    exit /b 1
)
if %GCC_MAJOR% LSS 10 (
    echo ERROR: Stockfish requires GCC 10 or newer. Found GCC %GCC_MAJOR%.
    echo Install the MSYS2 MINGW64 toolchain and add its mingw64\bin to PATH.
    exit /b 1
)

where sh >nul 2>nul
if errorlevel 1 (
    echo ERROR: A POSIX sh shell was not found on PATH.
    echo Add the MSYS2 usr\bin directory to PATH.
    exit /b 1
)

echo Building Stockfish. This may download its neural network the first time.
make -C src -j2 build ARCH=x86-64 COMP=gcc
if errorlevel 1 (
    echo ERROR: Stockfish build failed.
    exit /b 1
)
if not exist "src\stockfish.exe" (
    echo ERROR: The Stockfish build completed without producing src\stockfish.exe.
    exit /b 1
)

echo.
echo Installing Python packages...
"%PYTHON_EXE%" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Installing Python packages failed.
    exit /b 1
)

echo.
echo Running game tests...
"%PYTHON_EXE%" -m unittest discover -s tests -p "test_chess_game.py"
if errorlevel 1 (
    echo ERROR: Game tests failed.
    exit /b 1
)

echo.
echo Packaging Chess.exe...
"%PYTHON_EXE%" -m PyInstaller --noconfirm --clean --onefile --name Chess --distpath dist --workpath build\pyinstaller --specpath build chess_game.py
if errorlevel 1 (
    echo ERROR: Packaging Chess.exe failed.
    exit /b 1
)

copy /y "src\stockfish.exe" "dist\stockfish.exe" >nul
if errorlevel 1 (
    echo ERROR: Could not copy Stockfish into dist.
    exit /b 1
)

echo.
copy /y "README.md" "dist\README.txt" >nul
if errorlevel 1 (
    echo ERROR: Could not copy the portable-game instructions.
    exit /b 1
)
copy /y "Copying.txt" "dist\Copying.txt" >nul
if errorlevel 1 (
    echo ERROR: Could not copy the Stockfish license.
    exit /b 1
)

echo.
echo Creating Chess-portable.zip without Syzygy tablebases...
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference = 'Stop'; Compress-Archive -Path '.\dist\Chess.exe','.\dist\stockfish.exe','.\dist\README.txt','.\dist\Copying.txt' -DestinationPath '.\Chess-portable.zip' -Force"
if errorlevel 1 (
    echo ERROR: Creating Chess-portable.zip failed.
    exit /b 1
)
if not exist "Chess-portable.zip" (
    echo ERROR: The portable release archive was not created.
    exit /b 1
)

echo.
echo Portable release complete:
echo   Chess-portable.zip
echo   dist\Chess.exe
echo   dist\stockfish.exe
echo Copy Chess-portable.zip to the other Windows computer, extract all files,
echo and run Chess.exe. Keep all extracted files together.
echo Syzygy tablebases are not included.
exit /b 0
