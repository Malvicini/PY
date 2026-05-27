@echo off
REM Avvia il server Flask per l'app Archiviazione Particolari
cd /d %~dp0
start /b python app.py

echo =====================================================
echo Server Archivio Particolari avviato su http://localhost:9000
echo =====================================================
exit
