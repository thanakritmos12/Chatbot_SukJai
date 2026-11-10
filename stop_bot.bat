@echo off
echo กำลังหยุดการทำงานของบอทและ ngrok...
taskkill /F /IM ngrok.exe /T 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do taskkill /F /PID %%a 2>nul
echo หยุดระบบเรียบร้อยแล้วครับ
pause
