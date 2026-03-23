@echo off
REM Esegui Smista_PDF.bat e aspetta che finisca
echo =====================================================
echo Avvio smistamento PDF...
echo =====================================================
call "H:\96-GESTIONE_STUDI\Smista_PDF.bat"

echo.
echo =====================================================
echo PDF smistati. Avvio server Flask...
echo =====================================================
echo.

cd /d H:\96-GESTIONE_STUDI\PY
start /b python app.py

echo Server avviato in background su http://localhost:8000
echo.
exit