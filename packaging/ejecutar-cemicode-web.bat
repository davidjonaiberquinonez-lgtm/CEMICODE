@echo off
title CEMICODE Portable (web)
set "CEMICODE_HOME=%~dp0"
cd /d "%CEMICODE_HOME%"
if not exist ".env" copy /y ".env.example" ".env" >nul
start "" "%CEMICODE_HOME%bin\cemicode.exe" web
