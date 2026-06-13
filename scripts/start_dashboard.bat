@echo off
REM Launches the GG MMA Tank Dashboard. Starts a local web server (so the
REM browser can fetch status.json — Chrome blocks fetch on file:// URLs)
REM and opens the dashboard in your default browser.
REM
REM To stop: close this cmd window.
REM To pin as a real "desktop app": right-click this .bat -> Create shortcut
REM -> Pin to taskbar.

cd /d "%~dp0\.."
echo.
echo  GG MMA Tank Dashboard
echo  =====================
echo  Opening http://localhost:8765/dashboard.html in your browser...
echo  (close this window to stop the dashboard server)
echo.
start "" "http://localhost:8765/dashboard.html"
python -m http.server 8765 -d public
