@echo off
rem ============================================================
rem   Historique Nomade - lanceur Windows
rem   Double-cliquez sur ce fichier pour ouvrir l'outil.
rem ============================================================
setlocal
cd /d "%~dp0"

rem Essaie le lanceur "py -3", puis "python".
where py >nul 2>nul
if %errorlevel%==0 (
    py -3 history_tool.py %*
    goto :end
)
where python >nul 2>nul
if %errorlevel%==0 (
    python history_tool.py %*
    goto :end
)

echo.
echo   Python 3 est introuvable sur cet ordinateur.
echo.
echo   Installez-le gratuitement :
echo     - Microsoft Store : cherchez "Python 3"
echo     - ou https://python.org  (cochez "Add Python to PATH")
echo.
echo   Puis relancez ce fichier.
echo.
pause

:end
endlocal
