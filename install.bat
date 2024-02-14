@echo off
REM Change the next line to the path where you want to create your venv
set VENV_DIR=%~dp0venv

echo Creating virtual environment...
python -m venv %VENV_DIR%

echo Activating virtual environment...
call %VENV_DIR%\Scripts\activate.bat

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Running PyInstaller...
call pyinstaller --onefile --noconsole main.py

echo Deactivating virtual environment...
call %VENV_DIR%\Scripts\deactivate.bat

echo Done.
pause
