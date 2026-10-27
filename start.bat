@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  py -3.12 -m venv .venv
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -c "import mediapipe, cv2, PIL, pyvirtualcam; assert mediapipe.__version__ == '0.10.21'" >nul 2>&1
if errorlevel 1 (
  .venv\Scripts\python.exe -m pip install -r requirements-lock.txt
  if errorlevel 1 goto failed
)
.venv\Scripts\python.exe app.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo No se pudo iniciar. Revisa el mensaje de arriba. Se requiere Python 3.12.
pause
exit /b 1
